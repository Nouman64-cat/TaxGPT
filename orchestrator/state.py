from typing import Annotated, TypedDict, List
import operator

class GraphState(TypedDict):
    query: str
    route: str          # 'vector', 'graph', or 'hybrid'
    context: Annotated[List[str], operator.add]  # Retrieved documents/data
    answer: str
