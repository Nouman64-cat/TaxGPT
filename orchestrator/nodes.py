import os
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from state import GraphState
from tools import query_chroma, query_neo4j  # Custom tools to keep nodes DRY

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
    raw_route = response.content.strip().lower()
    # Normalize: only accept exact 'vector' or 'graph', default to 'hybrid'
    route = raw_route if raw_route in ("vector", "graph") else "hybrid"
    print(f"[ROUTER] Query: '{state['query']}' -> LLM said: '{raw_route}' -> Route: '{route}'")
    
    return {"route": route}

def vector_node(state: GraphState) -> GraphState:
    """Retrieves unstructured context from ChromaDB."""
    try:
        docs = query_chroma(state["query"])
        print(f"[VECTOR] Retrieved {len(docs)} chars: {docs[:200]}...")
        return {"context": [docs] if docs.strip() else []}
    except Exception as e:
        print(f"[VECTOR] Error: {e}")
        return {"context": []}

def graph_node(state: GraphState) -> GraphState:
    """Retrieves structured relationships from Neo4j."""
    try:
        data = query_neo4j(state["query"], llm)
        print(f"[GRAPH] Retrieved {len(data)} chars: {data[:200]}...")
        return {"context": [data] if data.strip() else []}
    except Exception as e:
        print(f"[GRAPH] Error: {e}")
        return {"context": []}

def synthesizer_node(state: GraphState) -> GraphState:
    """Generates the final hallucination-free answer."""
    raw_context = state.get("context", [])
    
    # Flatten any nested structures and filter empty strings
    flat = []
    for item in raw_context:
        if isinstance(item, list):
            flat.extend(str(x) for x in item)
        else:
            flat.append(str(item))
    context_str = "\n".join(c for c in flat if c.strip())
    
    print(f"[SYNTHESIZER] Context length: {len(context_str)} chars")
    print(f"[SYNTHESIZER] Context preview: {context_str[:500]}")
    
    prompt = PromptTemplate.from_template(
        "You are TaxGPT. Answer the user query using ONLY the provided context.\n"
        "Context: {context}\n"
        "Query: {query}\n"
        "Answer strictly based on facts provided."
    )
    chain = prompt | llm
    response = chain.invoke({"query": state["query"], "context": context_str})
    
    return {"answer": response.content}