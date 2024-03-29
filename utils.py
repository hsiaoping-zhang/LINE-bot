import os
import json

from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.models import ImageSendMessage, VideoSendMessage, LocationSendMessage, StickerSendMessage
from linebot.models import MessageAction

channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)


def send_text_message(reply_token, text):
	line_bot_api = LineBotApi(channel_access_token)
	#text += ":))"
	line_bot_api.reply_message(reply_token, TextSendMessage(text=text))

	return "OK"

def send_image_message(reply_token, img_url):
	channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
	line_bot_api = LineBotApi(channel_access_token)
	print("enter send_image_url function")
	print("img url:", img_url)
	message = {
		"type": "image",
		"originalContentUrl": img_url,
		"previewImageUrl": img_url
	}

	line_bot_api.reply_message(reply_token, ImageSendMessage(original_content_url=img_url, preview_image_url=img_url))

	return "OK"

def send_button_message(id, text, buttons):
	pass

