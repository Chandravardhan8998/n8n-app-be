import json

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionUserMessageParam

from app.models.models import Response, State, EvaluateCodeModel

EVALUATE_CODE="evaluate_code"

def evaluate_code(state:State):
    load_dotenv()
    print("evaluate_code",state)
    client = OpenAI()
    if state.get("last_step") == "start":
        code=state.get("prompt")
    else:
        code=state.get("response").get("message")
    SYSTEM_PROMPT = """
              You are a Coding Expert Agent and your job is to 
              1. Check if provided value is code
              2. If not code send is_code as false else true
              3. If provided prompt is code, evaluate the code thoroughly rate it out out of 1-10 
                    where 1 is lowest quality and 10 is highest quality
                    add a remark for betterment or appreciation (30 words limit.)
              """
    query_res = client.beta.chat.completions.parse(
        model="gpt-4.1-nano",
        response_format=EvaluateCodeModel,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            ChatCompletionUserMessageParam(role="user", content=code)
        ],
    )
    parsedResponse=query_res.choices[0].message.parsed
    parsedResponse.type=EVALUATE_CODE
    meta=parsedResponse.model_dump()
    response: Response = {
        "type": None,
        "message": code,
        "meta":json.dumps(meta)
    }
    state["response"] = response
    state["last_step"] = EVALUATE_CODE
    return state
