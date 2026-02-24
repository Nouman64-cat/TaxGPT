import os
import chromadb
from neo4j import GraphDatabase
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. Initialize DB Connections
neo4j_driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

chroma_client = chromadb.HttpClient(host="chroma_db", port=8000)
vector_store = Chroma(
    collection_name="tax_knowledge",
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-large"),
    client=chroma_client
)

# 2. Graph Ingestion Logic
def ingest_to_neo4j(records: list):
    """Batch inserts CSV rows into Neo4j Aura."""
    cypher_query = """
    UNWIND $batch AS row
    
    // Merge Entities (Nodes)
    MERGE (t:TaxpayerType {name: row.`Taxpayer Type`})
    MERGE (s:State {name: row.State})
    MERGE (i:IncomeSource {name: row.`Income Source`})
    MERGE (d:DeductionType {name: row.`Deduction Type`})
    
    // Create Transaction Node with Metrics
    CREATE (tx:Transaction {
        date: row.`Transaction Date`,
        year: row.`Tax Year`,
        income: toFloat(row.Income),
        deductions: toFloat(row.Deductions),
        taxable_income: toFloat(row.`Taxable Income`),
        tax_rate: toFloat(row.`Tax Rate`),
        tax_owed: toFloat(row.`Tax Owed`)
    })
    
    // Create Relationships
    MERGE (tx)-[:FILED_BY]->(t)
    MERGE (tx)-[:FILED_IN]->(s)
    MERGE (tx)-[:HAS_INCOME_SOURCE]->(i)
    MERGE (tx)-[:CLAIMED_DEDUCTION]->(d)
    """
    
    with neo4j_driver.session() as session:
        # Insert in batches of 1000 to optimize network payload
        batch_size = 1000
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            session.run(cypher_query, batch=batch)
            print(f"Inserted graph batch {i} to {i+len(batch)}")

# 3. Vector Ingestion Logic
def ingest_to_chroma(chunks: list):
    """Chunks and embeds text into ChromaDB with adaptive batching."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=128)
    
    texts = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]
    
    split_docs = text_splitter.create_documents(texts, metadatas=metadatas)
    total = len(split_docs)
    print(f"Total split documents: {total}")
    
    batch_size = 100  # Safe default for HTTP payload limits
    i = 0
    while i < total:
        batch = split_docs[i:i + batch_size]
        try:
            vector_store.add_documents(batch)
            print(f"Upserted batch {i} to {i + len(batch)} of {total}")
            i += len(batch)
        except Exception as e:
            if "413" in str(e) or "Payload too large" in str(e):
                batch_size = max(10, batch_size // 2)
                print(f"Payload too large, reducing batch size to {batch_size}")
            else:
                raise
    
    print(f"Upserted {total} total chunks into ChromaDB.")