import os

from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import ImageSendMessage, VideoSendMessage, LocationSendMessage, StickerSendMessage


channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)


def send_text_message(reply_token, text):
    line_bot_api = LineBotApi(channel_access_token)
    text += ":))"
    line_bot_api.reply_message(reply_token, TextSendMessage(text=text))

    return "OK"



def send_image_url(id, img_url):
	image_url = "https://i.imgur.com/eTldj2E.png?1"

	try:
		line_bot_api.push_message(id, ImageSendMessage(original_content_url=image_url, preview_image_url=image_url))
	
	except LineBotApiError as e:
		raise e

	return "OK"

def send_button_message(id, text, buttons):
    pass

