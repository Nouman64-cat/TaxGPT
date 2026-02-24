import os
import chromadb
from langchain_neo4j import Neo4jGraph
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# 1. Initialize Neo4j Graph Connection
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
    database=os.getenv("NEO4J_DATABASE", "neo4j")
)

# 2. Initialize ChromaDB Connection (remote container)
chroma_client = chromadb.HttpClient(host="chroma_db", port=8000)
vector_store = Chroma(
    collection_name="tax_knowledge",
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-large"),
    client=chroma_client
)
retriever = vector_store.as_retriever(search_kwargs={"k": 5})

def query_neo4j(query: str, llm) -> str:
    """Executes natural language queries against Neo4j using Cypher."""
    print(f"[NEO4J] Graph schema: {graph.schema}")
    chain = GraphCypherQAChain.from_llm(
        llm=llm, 
        graph=graph, 
        verbose=True,
        allow_dangerous_requests=True # Required for read-only Cypher generation
    )
    result = chain.invoke({"query": query})
    print(f"[NEO4J] Raw result: {result}")
    return result.get("result", "No relational data found.")

def query_chroma(query: str) -> str:
    """Retrieves semantic documents from ChromaDB."""
    docs = retriever.invoke(query)
    print(f"[CHROMA] Found {len(docs)} documents")
    for i, doc in enumerate(docs):
        print(f"[CHROMA] Doc {i}: {doc.page_content[:100]}...")
    return "\n".join([doc.page_content for doc in docs])