import os
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from state import GraphState
from tools import query_chroma, query_neo4j # Custom tools to keep nodes DRY

# Initialize Claude
llm = ChatAnthropic(
    model="claude-opus-4-20250514", 
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

def router_node(state: GraphState) -> GraphState:
    """Routes the query based on required data types."""
    prompt = PromptTemplate.from_template(
        "Analyze the query: '{query}'. "
        "If it requires numerical data, aggregations, or specific taxpayer records, output 'graph'. "
        "If it requires tax rules, forms, or legal definitions, output 'vector'. "
        "If both, output 'hybrid'. Output ONLY the single word."
    )
    chain = prompt | llm
    response = chain.invoke({"query": state["query"]})
    
    return {"route": response.content.strip().lower()}

def vector_node(state: GraphState) -> GraphState:
    """Retrieves unstructured context from ChromaDB."""
    docs = query_chroma(state["query"])
    return {"context": [docs]}

def graph_node(state: GraphState) -> GraphState:
    """Retrieves structured relationships from Neo4j."""
    data = query_neo4j(state["query"], llm) 
    return {"context": [data]}

def synthesizer_node(state: GraphState) -> GraphState:
    """Generates the final hallucination-free answer."""
    context_str = "\n".join(state.get("context", []))
    
    prompt = PromptTemplate.from_template(
        "You are TaxGPT. Answer the user query using ONLY the provided context.\n"
        "Context: {context}\n"
        "Query: {query}\n"
        "Answer strictly based on facts provided."
    )
    chain = prompt | llm
    response = chain.invoke({"query": state["query"], "context": context_str})
    
    return {"answer": response.content}