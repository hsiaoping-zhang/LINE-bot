import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import ImageSendMessage, VideoSendMessage, LocationSendMessage, StickerSendMessage

from fsm import TocMachine
from utils import send_text_message
from utils import send_image_url


load_dotenv()


machine = TocMachine(
    states=["user", "state1", "state2"],
    transitions=[
        {
            "trigger": "advance",
            "source": "user",
            "dest": "state1",
            "conditions": "is_going_to_state1",
        },
        {
            "trigger": "advance",
            "source": "user",
            "dest": "state2",
            "conditions": "is_going_to_state2",
        },
        {"trigger": "go_back", "source": ["state1", "state2"], "dest": "user"},
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)

app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)
# handler = WebhookHandler("LINE_CHANNEL_SECRET")

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        if("貼圖" in event.message.text):
            line_bot_api.reply_message(event.reply_token,StickerSendMessage(package_id=11537, sticker_id=52002738))

        event.message.text += " :)"
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text)
        )

    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")
        response = machine.advance(event)
        if response == False:
            send_text_message(event.reply_token, "Not Entering any State")

    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")

# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     msg = event.message.text
#     print(msg)
#     msg = msg.encode('utf-8')
#     if msg=="DOG":
#         line_bot_api.reply_message(event.reply_token,TextSendMessage(text="汪汪叫"))
#     if msg=="ian":
#         line_bot_api.reply_message(event.reply_token,TextSendMessage(text="甚麼"))
#     if msg=="lillian_hong":
#         line_bot_api.reply_message(event.reply_token,TextSendMessage(text="So cute"))
#     else:
#         line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
