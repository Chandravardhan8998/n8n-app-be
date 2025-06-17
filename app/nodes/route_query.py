from app.models.models import State
from langgraph.constants import END

ROUTE_QUERY="conditional_routing"

def route_query(state:State)->str:
    res=state.get("response")
    print("--- doing routing ",res.get("type"))
    if res:
        q_type=res.get("type")
        return q_type
    return END

