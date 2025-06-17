from app.models.models import State
SEND_MAIL="send_mail"

def send_mail(state:State):

    state["last_step"] = SEND_MAIL
    return state
