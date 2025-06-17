from app.nodes.classify_message import classify_message
from app.nodes.evaluate_code import evaluate_code
from app.nodes.route_query import route_query
from app.nodes.write_code import write_code
from app.nodes.write_mail_and_send import send_mail
from app.nodes.write_message import write_message

distribute={
    "conditional_routing":route_query,
    "write_code":write_code,
    "write_mail_and_send":send_mail,
    "write_message":write_message,
    "classify_message":classify_message,
    "evaluate_code":evaluate_code,
}