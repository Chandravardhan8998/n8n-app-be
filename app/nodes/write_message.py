from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionUserMessageParam

from app.models.models import State, Response

WRITE_MESSAGE="write_message"
def write_message(state:State):
    print("--- doing write_message")
    load_dotenv()
    client = OpenAI()
    query_res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            ChatCompletionUserMessageParam(role="user",content=state.get("prompt"))
        ]
    )
    message=""
    if query_res.choices[0].message.content:
        message=query_res.choices[0].message.content
    response: Response = {
        "type": None,
        "message": message,
        "meta":""
    }
    state["response"] = response
    state["last_step"] = WRITE_MESSAGE
    return state
