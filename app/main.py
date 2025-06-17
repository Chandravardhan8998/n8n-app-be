from bson import ObjectId
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


from app.db.mongo import node_collection, flow_collection
from app.models.models import CreateFlow, CreateNode, GraphData, Node, State, Response
from app.utils.utils import serialize_doc
from app.controllers.runflow import convert_edges_to_nodes, create_graph

app = FastAPI()
load_dotenv()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/test")
async  def test():
    return {"test":"test"}

@app.post("/create-flow")
async def create_flow(flow_data:CreateFlow):
    flow_dict = flow_data.model_dump()
    result = await flow_collection.insert_one(flow_dict)
    return {"msg": "Flow added", "id": str(result.inserted_id)}

@app.get("/flows")
async def get_flows():
    flows_cursor = flow_collection.find({})
    flows = []
    async for flow in flows_cursor:
        flows.append(serialize_doc(flow))
    return flows

@app.post("/run-flow")
async def run_flows_by_id(data:GraphData):
    user_flow=data.data
    nodes=await convert_edges_to_nodes(user_flow)
    print("----")
    print('-->',nodes)
    print("----")
    # return nodes
    conditionalSteps,graph=await create_graph(nodes)
    response:Response={
        "message":"",
        "type":None,
        "meta":""
    }
    _state: State = {
        "prompt": data.input,
        "possible_next_nodes":conditionalSteps,
        "response": response,
        "last_step":"start"
    }

    result = await graph.ainvoke(_state)
    print(result.get("response").get("message"))
    return result.get("response")


@app.post("/create-node")
async def create_node(node_data:CreateNode):
    node_dict = node_data.model_dump()
    result = await node_collection.insert_one(node_dict)
    return {"msg": "Node added", "id": str(result.inserted_id)}

@app.get("/system-nodes")
async def get_system_nodes():
    nodes_cursor = node_collection.find({})
    nodes = []
    async for node in nodes_cursor:
        nodes.append(serialize_doc(node))
    return nodes

@app.get("/system-nodes/{node_id}")
async def get_system_node_by_id(node_id:str):
    try:
        obj_id = ObjectId(node_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ObjectId")

    node = await node_collection.find_one({"_id": obj_id})
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return serialize_doc(node)

'''
Nodes
write code
write message
write email and send
convert message to md formate

Frontend:

Response: {  // for backend, no Response on frontend
            message:string, 
            type:node_type
        } 
Node: {
    id:string, 
    node_id:string, 
    prompt:string, 
    response:Response,
    flow_type: "linear" | "conditional",
    next_edge: node_id[]
}

flow_data:Node[] 
class Node(TypedDict):
    id: str
    node_id: str
    node_type: str
    prompt:str
    flow_type: str
    next_node_id: List[str]
[
    {
        id:"1j2uigbewiu2wke"
        node_id:"START", 
        prompt:"How are you?", 
        flow_type: "linear",
        next_edge: ["classify_message"]
    },
    {
        id:"12345678", 
        node_id:"classify_message", 
        prompt:"How are you?", 
        flow_type: "conditional",
        next_edge: ["write_message","write_code"]
    },
    {
        id:"12345678", 
        node_id:"write_code", 
        prompt:"How are you?", 
        flow_type: "linear"
        next_edge: ["evaluate_code"]
    },
    {
        id:"12345678", 
        node_id:"evaluate_code", 
        prompt:"How are you?", 
        flow_type: "linear"
        next_edge: ["END"]
    },
    {
        id:"12345678", 
        node_id:"write_message", 
        prompt:"How are you?", 
        flow_type: "linear"
        next_edge: ["END"]
    },
]


"next_nodes": ["write_code_id", "write_message_id"]

for every node
i will create a prompt like this 

nextNodeStepsCheck="Check if this prompt satisfy this below checks and along with response send the output of this check as type in JSON formate"
for next_node_id in node.next_nodes
    next_node = await db.get(next_node_id)
    nextNodeStepsCheck+=f"/n {next_node.what_i_do} return type as {next_node.type} if prompt satisfy this."
    
f"${node.prompt}/n/n/n ${nextNodeStepsCheck}" # this will return Eg: {response:"some message", type:"write_message"}
    "name": "Write Code",
    "type": "write_code",
    "gpt_model":"gpt-4.1",
    "llm": "openai",
    "description": "To write code based on prompt provided by user.",
    "what_i_do": "Check if the provided prompt satisfies this type 'write_code' if yes return type as 'write_code' else Ignore"
    
 {
      "id": "xy-edge__6-684a0a2a14df3de4f4f6845d-5-end",
      "source": "6-684a0a2a14df3de4f4f6845d",
      "target": "5-end"
    },    
'''
