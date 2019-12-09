import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage
from linebot.models import ImageSendMessage, VideoSendMessage, LocationSendMessage, StickerSendMessage

from fsm import TocMachine
from utils import send_text_message

from weather import get_weather

import random
#from utils import send_image_url


load_dotenv()

machine = TocMachine(
    states=["user", "state_send_1", "state_send_2", "state_send_3", "state_send_4_text", "state_send_4_img",
            "state_AQI", "state_add_user", "state_search_user",
             "state_quick_start", "state_recv_mail"],
    transitions=[
        {
            "trigger": "advance",
            "source": "user",
            "dest": "state_send_1",
            "conditions": "is_going_to_state_send_1",
        },
        {
            "trigger": "advance",
            "source": "state_send_1",
            "dest": "state_send_2",
            "conditions": "is_going_to_state_send_2",
        },
        {
            "trigger": "advance",
            "source": "state_send_2",
            "dest": "state_send_3",
            "conditions": "is_going_to_state_send_3",
        },
        {
            "trigger": "advance",
            "source": "state_send_3",
            "dest": "state_send_4_text",
            "conditions": "is_going_to_state_send_4_text",
        },
        {
            "trigger": "advance",
            "source": "state_send_3",
            "dest": "state_send_4_img",
            "conditions": "is_going_to_state_send_4_img",
        },
        {
            "trigger": "advance",
            "source": "user",
            "dest": "state_AQI",
            "conditions": "is_going_to_state_AQI",
        },
        {
            "trigger": "advance",
            "source": "user",
            "dest": "state_add_user",
            "conditions": "is_going_to_state_add_user",
        },
        {
            "trigger": "advance",
            "source": "user",
            "dest": "state_search_user",
            "conditions": "is_going_to_state_search_user",
        },
        {
            "trigger": "advance",
            "source": "user",
            "dest": "state_quick_start",
            "conditions": "is_going_to_state_quick_start",
        },
        {
            "trigger": "advance",
            "source": "user",
            "dest": "state_recv_mail",
            "conditions": "is_going_to_state_recv_mail",
        },
        {"trigger": "go_back", 
        "source": [ "state_send_4_text", "state_send_4_img",
                    "state_AQI", "state_add_user", "state_search_user", "state_quick_start", "state_recv_mail"], 
        "dest": "user"},
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
#handler = WebhookHandler("LINE_CHANNEL_SECRET")

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

        # if("貼圖" in event.message.text):
        #     sticker_list = range(52002734, 52002774)
        #     random_num = random.randint(0, 40)
        #     line_bot_api.reply_message(event.reply_token,StickerSendMessage(package_id=11537, sticker_id=sticker_list[random_num]))

        # elif("圖片" in event.message.text):
        #     image_url = "https://i.imgur.com/eTldj2E.png?1"
        #     line_bot_api.reply_message(event.reply_token, ImageSendMessage(original_content_url=image_url, preview_image_url=image_url))

        # elif("天氣" in event.message.text):
        #     weather_text = get_weather("2019")
        #     line_bot_api.reply_message(event.reply_token, TextSendMessage(text=weather_text))

        # elif("smile" in event.message.text):
        #     event.message.text += " :)"

        print("line reply")
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

        send_type = event.message
        if not (isinstance(send_type, TextMessage) or isinstance(send_type, ImageMessage)):
            continue
        
        # if not isinstance(event.message.text, str):
        #     continue

        # do not echo
        print("message:", event.message)
        if(isinstance(event.message, TextMessage)):
            if("#" in event.message.text):
                print("# enter")
                return "OK"
        else:
            print("type is not text")

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
#     # get user id
#     user_id = event.source.user_id
#     print("user id =", user_id)

#     line_bot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text))

if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
