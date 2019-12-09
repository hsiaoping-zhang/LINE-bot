from transitions.extensions import GraphMachine

from utils import send_text_message
from utils import send_image_message
from utils import quick_reply_message
from weather import get_weather
from firebase import add_user
from firebase import search_user
from firebase import send_mailbox
from firebase import recv_mailbox
from firebase import add_to_sendbox

from image_manage import upload_image

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)
        #print("init variable")
        self.tmp_receiver_name = ""
        self.tmp_content_type = "text"
        self.quiet_state = False

    # def is_going_to_state_AQI(self, event):
    #     # air quality
    #     print("AQI state")
    #     if(event.message.type == "image"):
    #         return False
    #     text = event.message.text
    #     return ("AQI" in text)

    def is_going_to_state_quiet(self, event):
        print("be quiet")
        if(self.quiet_state == True):
            return True
        if(event.message.type == "image"):
            return False
        
        text = event.message.text
        return "小小幫手休息" == text


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

    def is_going_to_state_add_user(self, event):
        # user id
        print("user id state")
        if(event.message.type == "image"):
            return False
        text = event.message.text
        return "user-id" in text.lower()

    def is_going_to_state_search_user(self, event):
        # user id
        print("user search state")
        if(event.message.type == "image"):
            return False
        text = event.message.text
        return "search-user" in text.lower()

    def is_going_to_state_quick_start(self, event):
        print("enter quick_start")
        if(event.message.type == "image"):
            return False
        text = event.message.text
        return "quick start" in text.lower()

    def is_going_to_state_recv_mail(self, event):
        print("enter recv mail")
        if(event.message.type == "image"):
            return False
        text = event.message.text
        return "recv-mail" in text.lower()

    # on enter state #

    def on_enter_state_send_1(self, event):
        print("I'm entering state send 1")
        reply_token = event.reply_token
        send_text_message(reply_token, "你想要送給誰?")
        # self.go_back()

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
        # 判斷圖片
        send_text_message(reply_token, "開始寫訊息傳給我吧~")

    # 文字訊息
    def on_enter_state_send_4_text(self, event):
        print("I'm entering state send 4 text")
        receiver_name = self.tmp_receiver_name
        sender_id = str(event.source.user_id)
        content = event.message.text
        return_text = send_mailbox(receiver_name, sender_id, self.tmp_content_type, content)
        reply_token = event.reply_token
        send_text_message(reply_token, return_text)

        self.tmp_receiver_name = ""
        self.tmp_content_type = ""
        self.go_back()

    # 圖片訊息
    def on_enter_state_send_4_img(self, event):
        print("I'm entering state send 4 img")
        receiver_name = self.tmp_receiver_name
        sender_id = str(event.source.user_id)
        img_id = event.message.id
        img_url = upload_image(sender_id, receiver_name, img_id)
        return_text = send_mailbox(receiver_name, sender_id, self.tmp_content_type, img_url)
        return_text = "[圖片] " + return_text

        reply_token = event.reply_token
        send_text_message(reply_token, return_text)

        self.tmp_receiver_name = ""
        self.tmp_content_type = ""
        self.go_back()

    def on_enter_state_quiet(self, event):
        print("I'm entering state2")

        self.quiet_state = True
        # reply_token = event.reply_token
        # send_text_message(reply_token, "Trigger state2")
        # self.go_back()

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

    def on_enter_state_quick_start(self, event):
        print("I'm entering quick_start")
        reply_token = event.reply_token
        quick_reply_message(reply_token)
        print("quick reply success")
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

        self.go_back()

    # on exit state #

    def on_exit_state_send_1(self, event):
        print("Leaving state send 1")

    def on_exit_state_send_2(self, event):
        print("Leaving state send 2")

    def on_exit_state_send_3(self, event):
        print("Leaving state send 3")

    def on_exit_state_send_4_text(self):
        print("Leaving state send 4 text")

    def on_exit_state_send_4_img(self):
        print("Leaving state send 4 img")

    def on_exit_state_quiet(self):
        print("Leaving state quiet")

    def on_exit_state_add_user(self):
        print("Leaving state_add_user")

    def on_exit_state_search_user(self):
        print("Leaving state_search_user")

    def on_exit_state_quick_start(self):
        print("Leaving state quick_start")

    def on_exit_state_recv_mail(self):
        print("Leaving state recv mail")



    
