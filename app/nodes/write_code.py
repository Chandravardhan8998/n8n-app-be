from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionUserMessageParam

from app.models.models import State, Response

WRITE_CODE="write_code"

def write_code(state:State):
    load_dotenv()
    client = OpenAI()
    print("write_code")
    SYSTEM_PROMPT = """
            You are a Coding Expert Agent
            Your job is to write code only 
            if provided prompt is not for code generation just skip by saying not able to generate code 
            no need to add any extra text or message for user like how to use and other docs you can add code comments only 
        """
    query_res = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            ChatCompletionUserMessageParam(role="user", content=state.get("prompt"))
        ]
    )
    message = ""
    if query_res.choices[0].message.content:
        message = query_res.choices[0].message.content
    response: Response = {
        "type": None,
        "message": message,
        "meta": ""
    }
    state["response"] = response
    state["last_step"] = WRITE_CODE
    return state
