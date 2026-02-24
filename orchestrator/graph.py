from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from nodes import router_node, vector_node, graph_node, synthesizer_node

# 1. Define the State
class GraphState(TypedDict):
    query: str
    route: str          # 'vector', 'graph', or 'hybrid'
    context: List[str]  # Retrieved documents/data
    answer: str

# 2. Initialize Graph
workflow = StateGraph(GraphState)

# 3. Add Nodes
workflow.add_node("router", router_node)
workflow.add_node("vector_retriever", vector_node)
workflow.add_node("graph_retriever", graph_node)
workflow.add_node("synthesizer", synthesizer_node)

# 4. Define Routing Logic
def route_query(state: GraphState):
    if state["route"] == "vector":
        return "vector_retriever"
    elif state["route"] == "graph":
        return "graph_retriever"
    return ["vector_retriever", "graph_retriever"] # Hybrid concurrent routing

# 5. Build Edges
workflow.set_entry_point("router")
workflow.add_conditional_edges("router", route_query)

# Both retrievers flow into the synthesizer
workflow.add_edge("vector_retriever", "synthesizer")
workflow.add_edge("graph_retriever", "synthesizer")
workflow.add_edge("synthesizer", END)

# 6. Compile
app = workflow.compile()