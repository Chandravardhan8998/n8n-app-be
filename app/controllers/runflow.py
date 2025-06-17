from collections import defaultdict
from typing import List, Tuple
from bson import ObjectId
from langgraph.constants import START,END
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from app.models.models import UserEdge
from app.db.mongo import node_collection
from app.nodes.classify_message import CLASSIFY_MESSAGE, classify_message
from app.nodes.distribute import distribute
from app.models.models import  Node, State


async def convert_edges_to_nodes(edges: List[UserEdge]) -> List[Node]:
    node_map = defaultdict(list)

    # Step 1: Build mapping of source -> list of targets
    for edge in edges:
        source = edge["source"]
        target = edge["target"]
        node_map[source].append(target)

    result: List[Node] = []
    for source_node_id, targets in node_map.items():
        node_id=source_node_id.split("-")[1]
        node = await node_collection.find_one({"_id":ObjectId(node_id)},{"_id":0,"type": 1})
        node_type = node.get("type")

        # Flow type based on node_type
        flow_type = "conditional" if (len(targets)>1) else "linear"

        # Node ID and ID field logic
        node_id = source_node_id
        generated_id = node_id + "-" + "-".join(targets)

        node: Node = {
            "id": generated_id,
            "node_id": node_id,
            "node_type": node_type,
            "prompt": "",  # placeholder
            "flow_type": flow_type,
            "next_node_id": targets
        }

        result.append(node)

    return result

async def create_graph(nodes:List[Node])->Tuple[List[str],CompiledStateGraph]:
    graph_builder = StateGraph(State)

    # CREATE NODES
    classify_count=1
    for node in nodes:
        req: Node = node
        node_graph_id=req.get("node_id")
        node_db_id=node_graph_id.split('-')[1]
        node_type_tool = distribute.get(req.get("node_type"))
        is_conditional = req.get("flow_type") == "conditional"
        node_data=await node_collection.find_one({"_id":ObjectId(node_db_id)},{"_id":0,"category": 1})

        if is_conditional:

            print(f"61: graph_builder.add_node({classify_count}-{CLASSIFY_MESSAGE},{classify_message})")
            graph_builder.add_node(f"{classify_count}-{CLASSIFY_MESSAGE}",classify_message)
            classify_count=classify_count+1
        if node_data.get("category")!="initiate":
            print(f"63: graph_builder.add_node({node_graph_id},{node_type_tool})")
            graph_builder.add_node(node_graph_id,node_type_tool)


    # CREATE EDGES
    conditional_routes_list=[]
    classification_id_tracker=dict()
    classify_count_edge=0
    for node in nodes:
        req: Node = node
        node_type = req.get("node_type")

        is_start = node_type == "on_prompt"
        is_conditional = req.get("flow_type") == "conditional"
        next_edge_graph_id=node.get('next_node_id')[0]
        next_edge_db_id=next_edge_graph_id.split("-")[1]
        next_edge_data=await node_collection.find_one({"_id":ObjectId(next_edge_db_id)},{"_id":0,"category": 1,"type":1})

        if is_start:
            if next_edge_data.get("category")=='conditional':
                # manage classification id
                classification_id = ""
                for key, value in classification_id_tracker.items():
                    if not value:
                        classification_id = key
                        classification_id_tracker[classification_id] = True
                if classification_id == "":
                    classify_count_edge = classify_count_edge + 1
                    classification_id = f"{classify_count_edge}-{CLASSIFY_MESSAGE}"
                    classification_id_tracker[classification_id] = False
                # manage classification id

                print(f"82: graph_builder.add_edge({START},{classification_id})")
                graph_builder.add_edge(START,classification_id)
            else:
                print(f"85: graph_builder.add_edge({START},{next_edge_graph_id})")
                graph_builder.add_edge(START,next_edge_graph_id)
        elif is_conditional:
            next_routing_tool=distribute.get(req.get("node_type"))
            # manage classification id
            classification_id = ""
            for key, value in classification_id_tracker.items():
                if not value:
                    classification_id = key
                    classification_id_tracker[classification_id] = True
            if classification_id == "":
                classify_count_edge = classify_count_edge + 1
                classification_id = f"{classify_count_edge}-{CLASSIFY_MESSAGE}"
                classification_id_tracker[classification_id] = False
            # manage classification id

            print(f"89: graph_builder.add_conditional_edges({classification_id}, {next_routing_tool})")
            graph_builder.add_conditional_edges(classification_id, next_routing_tool)
            for n in node.get("next_node_id"):
                conditional_routes_list.append(n)
        else:
            start_edge_graph_id=node.get('node_id')
            if next_edge_data.get("category")=='conditional':
                # manage classification id
                classification_id = ""
                for key, value in classification_id_tracker.items():
                    if not value:
                        classification_id = key
                        classification_id_tracker[classification_id] = True
                if classification_id == "":
                    classify_count_edge = classify_count_edge + 1
                    classification_id = f"{classify_count_edge}-{CLASSIFY_MESSAGE}"
                    classification_id_tracker[classification_id] = False
                # manage classification id
                print(f"96: graph_builder.add_edge({start_edge_graph_id},{classification_id})")
                graph_builder.add_edge(start_edge_graph_id,classification_id)
            elif next_edge_data.get("category")=='close':
                print(f"99: graph_builder.add_edge({start_edge_graph_id},{END})")
                graph_builder.add_edge(start_edge_graph_id,END)
            else:
                print(f"102: graph_builder.add_edge({start_edge_graph_id},{next_edge_graph_id})")
                graph_builder.add_edge(start_edge_graph_id,next_edge_graph_id)

    print("103: conditional_routes_list: ",conditional_routes_list)
    # return conditional_routes_list
    return conditional_routes_list,graph_builder.compile()