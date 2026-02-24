import os
from langchain_community.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# 1. Initialize Neo4j Graph Connection
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD")
)

# 2. Initialize ChromaDB Connection
vector_store = Chroma(
    collection_name="tax_knowledge",
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-large"),
    # Point to the local ChromaDB container
    persist_directory=None, 
    client_settings={"chroma_api_impl": "rest", "chroma_server_host": "chroma_db", "chroma_server_http_port": "8000"}
)
retriever = vector_store.as_retriever(search_kwargs={"k": 5})

def query_neo4j(query: str, llm) -> str:
    """Executes natural language queries against Neo4j using Cypher."""
    chain = GraphCypherQAChain.from_llm(
        llm=llm, 
        graph=graph, 
        verbose=True,
        allow_dangerous_requests=True # Required for read-only Cypher generation
    )
    result = chain.invoke({"query": query})
    return result.get("result", "No relational data found.")

def query_chroma(query: str) -> str:
    """Retrieves semantic documents from ChromaDB."""
    docs = retriever.invoke(query)
    return "\n".join([doc.page_content for doc in docs])