from typing import TypedDict, List

class GraphState(TypedDict):
    query: str
    route: str          # 'vector', 'graph', or 'hybrid'
    context: List[str]  # Retrieved documents/data
    answer: str
