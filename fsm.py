from transitions.extensions import GraphMachine
from linebot import LineBotApi
from linebot.exceptions import LineBotApiError
from linebot.models import TextSendMessage
import os
import sys

from utils import send_text_message
from utils import send_image_message
from weather import get_weather
from firebase import add_user, search_user 
from firebase import send_mailbox, recv_mailbox, delete_mail
from firebase import get_mailbox_info

from image_manage import upload_image

from config import line_channel_access_token


class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)
        #print("init variable")
        self.tmp_receiver_name = ""
        self.tmp_content_type = "text"
        self.quiet_state = False
        self.content = ""
        self.name_mode = ""
        self.get_mail_id = ""

    def init_variable(self):
        self.tmp_receiver_name = ""
        self.tmp_content_type = "text"
        self.quiet_state = False
        self.content = ""
        self.name_mode = ""
        self.get_mail_id = ""

    def is_going_to_state_quiet(self, event):
        print("self.quiet_state:", self.quiet_state)
        if((self.quiet_state == True) and (event.message.type == "text") and ("小小幫手起床" in event.message.text)):
            print("quiet break")
            self.quiet_state = False
            return False
        elif(self.quiet_state == True):
            print("quiet stay")
            return True
        if(event.message.type == "image"):
            return False
        
        text = event.message.text
        return "小小幫手休息" in text

    def is_going_to_state_recover(self, event):
        print("recover!!")
        # only with quiet to implement
        if((self.quiet_state == True) and (event.message.type == "text") and ("小小幫手起床" in event.message.text)):
            print("change quiet")
            self.init_variable()
            return True
        return False

    # 要求送信請求
    def is_going_to_state_send_1(self, event):
        print("enter state: send 1")
        if(event.message.type == "image"):
            return False
        text = event.message.text
        return ("送信" in text or "寫信" in text)

    # 產生收件人
    def is_going_to_state_send_2(self, event):
        print("enter state: send 2")
        if(event.message.type == "image"):
            return False
        text = event.message.text
        if(text == "取消" or text == "cancel"):
            return False
        # store recciver name
        print("setting tmp_receiver_name")
        self.tmp_receiver_name = text
        # elif(text == "名單" or text == "list"):
        return True

    # 信的形式
    def is_going_to_state_send_3(self, event):
        print("enter state: send 3")
        if(event.message.type == "image"):
            return False
        text = event.message.text
        if(text == "文字"):
            self.tmp_content_type = "text"
        elif((text == "圖片") or (text == "img") or (text == "image")):
            print("revise tmp_content_type")
            self.tmp_content_type = "img"
        return True

    def is_going_to_state_send_4_text(self, event):
        print("enter state: send 4 text")
        if(event.message.type == "image"):
            return False
        print("tmp_content_type:", self.tmp_content_type)
        self.tmp_content_type = event.message.type

        if(self.tmp_content_type == "img"):
            return False
        return True

    def is_going_to_state_send_4_img(self, event):
        print("enter state: send 4 img")
        if(self.tmp_content_type == "text"):
            return False
        return True

    def is_going_to_state_select_name(self, event):
        print("enter select name mode.")
        if(event.message.type == "image"):
            return False
        return True

    def is_going_to_state_select_date(self, event):
        print("enter select date mode.")
        if(event.message.type == "image"):
            return False
        text = event.message.text
        if(text != "無" and text.count(" ") != 2 and text[4] != " "):
            print("date input error")
            return False
        return True

    def is_going_to_state_add_user(self, event):
        # user id
        print("user id state")
        if(event.message.type == "image"):
            return False
        text = event.message.text
        return "新增" in text

    def is_going_to_state_search_user(self, event):
        # user id
        print("user search state")
        if(event.message.type == "image"):
            return False
        text = event.message.text
        return "搜尋" in text

    def is_going_to_state_recv_mail(self, event):
        print("enter recv mail")
        if(event.message.type == "image"):
            return False
        text = event.message.text
        return "收信" in text

    def is_going_to_state_delete_mail(self, event):
        print("delete mail")
        if(event.message.type == "image"):
            return False
        text = event.message.text
        print("del:", text)
        text_list = ["是", "否"]
        print(text in text_list)
        return (text in text_list)

    # air quality
    def is_going_to_state_AQI(self, event):
        print("空氣品質 state")
        if(event.message.type == "image"):
            return False
        text = event.message.text
        return ("空氣品質" in text)


    # on enter state #

    def on_enter_state_quiet(self, event):
        print("be quiet")
        reply_token = event.reply_token
        self.quiet_state = True
        if(self.quiet_state == False):
            send_text_message(reply_token, "好的好的，我去休息了")
            self.quiet_state = True
        else:
            pass

    def on_enter_state_recover(self, event):
        reply_token = event.reply_token
        self.quiet_state = False
        send_text_message(reply_token, "小小幫手甦醒囉~")
        print("go back")
        self.go_back()


    def on_enter_state_send_1(self, event):
        print("I'm entering state send 1")
        reply_token = event.reply_token
        send_text_message(reply_token, "你想要送給誰?")

    # 產生收件人
    def on_enter_state_send_2(self, event):
        print("I'm entering state send 2")
        self.tmp_receiver_name = event.message.text
        reply_token = event.reply_token
        send_text_message(reply_token, "形式是什麼? 文字(text) / 圖片(img)")

    # 信的形式
    def on_enter_state_send_3(self, event):
        print("I'm entering state send 3")
        reply_token = event.reply_token
        text = event.message.text
        text_list = ["文字", "text", "圖片", "img"]
        if(text not in text_list):
            return False
        send_text_message(reply_token, "開始寫訊息傳給我吧~")

    # 文字訊息
    def on_enter_state_send_4_text(self, event):
        print("I'm entering state send 4 text")
        receiver_name = self.tmp_receiver_name
        sender_id = str(event.source.user_id)
        self.content = event.message.text
        # NULL task
        reply_token = event.reply_token

        try:
            line_bot_api = LineBotApi(line_channel_access_token)
            line_bot_api.push_message(event.source.user_id, TextSendMessage(text="[文字訊息]已接收"))
        except LineBotApiError as e:
            raise e
        send_text_message(reply_token, "署名： (如果想匿名直接輸入匿名)")


    # 圖片訊息
    def on_enter_state_send_4_img(self, event):
        print("I'm entering state send 4 img")
        receiver_name = self.tmp_receiver_name
        sender_id = str(event.source.user_id)
        img_id = event.message.id
        self.content = upload_image(sender_id, receiver_name, img_id)

        # channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
        # line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
        try:
            line_bot_api = LineBotApi(line_channel_access_token)
            line_bot_api.push_message(event.source.user_id, TextSendMessage(text="[圖片訊息]已接收"))
        except LineBotApiError as e:
            raise e
        reply_token = event.reply_token
        send_text_message(reply_token, "署名： (如果想匿名直接輸入匿名)")

    # 選擇名字匿名與否
    def on_enter_state_select_name(self, event):
        reply_token = event.reply_token
        print("enter select name mode")
        self.name_mode = event.message.text
        # return_text = send_mailbox(receiver_name, sender_id, self.tmp_content_type, img_url)
        # channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
        line_bot_api = LineBotApi(line_channel_access_token)
        try:
            line_bot_api.push_message(event.source.user_id, TextSendMessage(text="已記錄"))
        except LineBotApiError as e:
            # error handle
            raise e
        send_text_message(reply_token, "日期模式\n(無：隨寄隨收 / 20XX XX XX：未來信)\n- - -\n如果日期小於今天，一樣視同「無」")

    # 選擇日期
    def on_enter_state_select_date(self, event):
        reply_token = event.reply_token
        print("enter select date mode")
        receiver_name = self.tmp_receiver_name
        sender_id = str(event.source.user_id)
        content_type = self.tmp_content_type
        content = self.content
        name_mode = self.name_mode
        date_mode = event.message.text

        return_text = send_mailbox(receiver_name, sender_id, content_type, content, name_mode, date_mode)
        send_text_message(reply_token, return_text)

        self.init_variable()
        self.go_back()

    def on_enter_state_add_user(self, event):
        reply_token = event.reply_token
        print("enter user id state")
        user_id = str(event.source.user_id)
        message = event.message.text
        user_name = message[message.index(" ")+1:]

        return_text = add_user(user_id, user_name)
        send_text_message(reply_token, return_text)
        self.go_back()

    def on_enter_state_search_user(self, event):
        reply_token = event.reply_token
        print("enter user search state")
        message = event.message.text
        search_user_name = message[message.index(" ")+1:]
        print("search user:%s" % (search_user_name))
        return_text = search_user(search_user_name)
        send_text_message(reply_token, return_text)
        self.go_back()


    def on_enter_state_recv_mail(self, event):
        print("I'm entering recv mail")
        reply_token = event.reply_token
        sender_name, content, date = recv_mailbox(str(event.source.user_id))
        return_text = "來自 " + sender_name + " 的訊息\n- - -\n" + content + "\n- - -\n時間 : " + date

        if(content == "fail"):
            return_text = "no message"
            send_text_message(reply_token, return_text)
        elif(content == "img"):
            print("It's image message")
            send_image_message(reply_token, sender_name)
        else:
            send_text_message(reply_token, return_text)

        line_bot_api = LineBotApi(line_channel_access_token)
        try:
            line_bot_api.push_message(event.source.user_id, TextSendMessage(text="是否刪除這則訊息(是 / 否)"))
        except LineBotApiError as e:
            # error handle
            raise e
        self.get_mail_id = date
        #self.go_back()

    def on_enter_state_delete_mail(self, event):
        print("delete mail.")
        reply_token = event.reply_token
        if(event.message.text == "是"):
            delete_mail(event.source.user_id, self.get_mail_id)
            send_text_message(reply_token, "已刪除")
        else:
            send_text_message(reply_token, "保存!!")
        
        self.init_variable()
        self.go_back()

    def on_enter_state_AQI(self, event):
        print("enter AQI state")
        reply_token = event.reply_token
        string = event.message.text
        print(string[string.index(" ")+1:])
        return_text = get_weather(string[string.index(" ")+1:])
        send_text_message(reply_token, return_text)
        self.go_back()


    # on exit state #

    def on_exit_state_send_1(self, event):
        print("Leaving state send 1")

    def on_exit_state_send_2(self, event):
        print("Leaving state send 2")

    def on_exit_state_send_3(self, event):
        print("Leaving state send 3")

    def on_exit_state_send_4_text(self, event):
        print("Leaving state send 4 text")

    def on_exit_state_send_4_img(self, event):
        print("Leaving state send 4 img")

    def on_exit_state_select_name(self, event):
        print("Leaving state select name")

    def on_exit_state_select_date(self):
        print("Leaving state selcet date")

    def on_exit_state_quiet(self, event):
        print("Leaving state quiet")

    def on_exit_state_recover(self):
        print("Leaving state recover")

    def on_exit_state_add_user(self):
        print("Leaving state_add_user")

    def on_exit_state_search_user(self):
        print("Leaving state_search_user")

    def on_exit_state_recv_mail(self, event):
        print("Leaving state recv mail")

    def on_exit_state_delete_mail(self):
        print("Leaving state delete mail")



    
