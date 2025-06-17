from typing import List

from langgraph.graph import StateGraph
from models.models import Node,State
from nodes.distribute import distribute
from nodes.route_query import route_query

data:List[Node]=[
    {
        "id":"1j2uigbewiu2wke",
        "node_id":"START",
        "node_type":"START",
        "prompt":"How are you?",
        "flow_type": "linear",
        "next_node_id": ["classify_message"]
    },
    {
        "id":"12345678",
        "node_id":"classify_message",
        "node_type":"classify_message",
        "prompt":"How are you?",
        "flow_type": "conditional",
        "next_node_id": ["write_message","write_code"]
    },
    {
        "id":"12345678",
        "node_id":"write_code",
        "node_type":"write_code",
        "prompt":"How are you?",
        "flow_type": "linear",
        "next_node_id": ["evaluate_code"]
    },
    {
        "id":"12345678",
        "node_id":"evaluate_code",
        "node_type":"evaluate_code",
        "prompt":"How are you?",
        "flow_type": "linear",
        "next_node_id": ["END"]
    },
    {
        "id":"12345678",
        "node_id":"write_message",
        "node_type":"write_message",
        "prompt":"How are you?",
        "flow_type": "linear",
        "next_node_id": ["END"]
    },
]


_state: State = {
 "prompt":"Write a message",
    "response":None
}
graph_builder = StateGraph(State)
# Define Nodes here
# graph_builder.add_node("classify_message", classify_message)
# graph_builder.add_node("route_query", route_query)
# graph_builder.add_node("general_query", general_query)
# graph_builder.add_node("coding_query", coding_query)
# graph_builder.add_node("coding_validate_query", coding_validate_query)
#
#
# graph = graph_builder.compile()
# return graph
is_route_query_added=False
for node in data:
    req:Node=node

    function_tool_name  =   req.get("node_type")
    function_tool   =   distribute.get(req.get("node_type"))
    is_conditional  =   req.get("flow_type")    ==  "conditional"
    if is_conditional:
        print(f"graph_builder.add_node('route_query',route_query)")
        is_route_query_added=True
    if function_tool_name != "START" and function_tool_name != "END":
        print(f"graph_builder.add_node('{function_tool_name}',{function_tool_name})")

# class Node(TypedDict):
#     id: str
#     node_id: str
#     prompt:str
#     flow_type: str
#     next_node_id: List[str]
# # Define Edges from START to END
# graph_builder.add_edge(START, "classify_message")
# graph_builder.add_conditional_edges("classify_message", route_query)
# graph_builder.add_edge("general_query", END)
#
# graph_builder.add_edge("coding_query", "coding_validate_query")
# graph_builder.add_edge("coding_validate_query", END)
#   {
#         "id":"1j2uigbewiu2wke",
#         "node_id":"START",
#         "node_type":"START",
#         "prompt":"How are you?",
#         "flow_type": "linear",
#         "next_node_id": ["classify_message"]
#     },
#     {
#         "id":"12345678",
#         "node_id":"classify_message",
#         "node_type":"classify_message",
#         "prompt":"How are you?",
#         "flow_type": "conditional",
#         "next_node_id": ["write_message","write_code"]
#     },
print("---------")
print("---------")
for node in data:
    req:Node=node
    node_type    =   req.get("node_type")
    is_start    =   node_type    ==  "START"
    is_conditional  =   req.get("flow_type")    ==  "conditional"
    next_node=None
    if is_conditional:
        next_node = route_query
    else:
        if req.get("next_node_id")[0]=="classify_message":
            next_node = "classify_message"
        if req.get("next_node_id")[0]=="END":
            next_node = "END"
        node_name_by_id=req.get("next_node_id")[0] # TODO:get this node's type from DB
        next_node = node_name_by_id
    if is_start:
        print(f"graph_builder.add_edge(START, '{next_node}')")
    else:
        print(f"graph_builder.add_edge({node_type}, '{next_node}')")




# print(graph_builder)
