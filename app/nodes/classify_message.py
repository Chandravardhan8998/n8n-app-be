from bson import ObjectId
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionUserMessageParam

from app.db.mongo import node_collection
from app.models.models import State, Response, ResponseModel

CLASSIFY_MESSAGE="classify_message"
async def classify_message(state:State):
    print("--- doing classification")
    load_dotenv()
    client = OpenAI()
    next_nodes=state.get("possible_next_nodes")
    print(next_nodes)

    nextNodeStepsCheck =""
    typeMap=dict()
    for p_node in next_nodes:
        node_id=p_node.split("-")[1]
        node_id_prefix=p_node.split("-")[0]
        node = await node_collection.find_one({"_id": ObjectId(node_id)}, {"_id": 0,"type":1, "what_i_do": 1})
        prefixed_type=f"{node_id_prefix}-{node.get("type")}"
        typeMap[prefixed_type]=p_node

        # FIX THIS PROMPT SO AI CAN DIFFERENTIATE BETWEEN TWO SAME types
        nextNodeStepsCheck += f"/n {prefixed_type}: {node.get("what_i_do")} and this `{node_id_prefix}` as prefix"

    # SYSTEM_PROMPT=f"""Check if this prompt satisfy this below checks and along with response send the output of this check as type in JSON formate
    #     PROMPT-START:
    #     {state.get("prompt")}
    #     PROMPT-END:
    #     -- Check for this
    #     {nextNodeStepsCheck}
    #     """
    query_res = client.beta.chat.completions.parse(
        model="gpt-4.1-nano",
        response_format=ResponseModel,
        messages=[
            {"role": "system", "content": nextNodeStepsCheck},
            ChatCompletionUserMessageParam(role="user", content=state.get("prompt"))
        ],
    )
    prompt_type=query_res.choices[0].message.parsed.type
    prompt_prefix=query_res.choices[0].message.parsed.prefix
    route_id=f"{prompt_prefix}-{prompt_type}"
    print("prompt_type ",route_id,typeMap[route_id])
    response: Response = {
        "type":typeMap[route_id],
        "message": state.get("response").get('message'),
        "meta": ""
    }
    state["response"] = response
    state["last_step"] = CLASSIFY_MESSAGE
    return state
