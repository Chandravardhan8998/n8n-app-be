from typing import List, Literal

from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class CreateFlow(BaseModel):
    name: str = Field(..., min_length=2, max_length=20)
    description: str = Field(..., min_length=2, max_length=100)
    data: str #JSON stringify
    """
        nodes:Node[]
        edges:Edge[]
        NodeInputState:
            prompt: string
            result: string
            is_success: boolean
            helping_data: 
        Node:
        
            tool:tool_id
            state:NodeInputState
            
            //Every node will take specific system decided state and return same type of state        
    """

class CreateNode(BaseModel):
    name: str = Field(..., min_length=2, max_length=20)
    type: str = Field(..., min_length=2, max_length=20)
    gpt_model:str = Field(..., min_length=2, max_length=20)
    llm:str = Field(..., min_length=2, max_length=20)
    description: str = Field(..., min_length=2, max_length=100)
    what_i_do:str # only use if conditional, using this in prompt will return that the prompt satisfy what i do or not if yes return "type" else None


class UserEdge(TypedDict):
    id:str
    source:str
    target:str

class GraphData(BaseModel):
    data:List[UserEdge]
    input:str

class Node(TypedDict):
    id: str
    node_id: str
    node_type: str
    prompt:str
    flow_type: str
    next_node_id: List[str]

class Response(TypedDict):
    message:str|None
    type:str|None
    meta:str|None

class ResponseModel(BaseModel):
    type:str
    prefix:int

class EvaluateCodeModel(BaseModel):
    rating:int
    is_code:bool
    remark:str
    type:str

class State(TypedDict):
    prompt: str
    response: Response
    last_step:None|str
    possible_next_nodes:List[str]|None


