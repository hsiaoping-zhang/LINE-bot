import firebase_admin 
from firebase_admin import credentials 
from firebase_admin import firestore

from datetime import date
from datetime import datetime

def get_db():
	print("enter initialize function")
	if (not len(firebase_admin._apps)):
		cred = credentials.Certificate('./linebot-helper-firebase-adminsdk-bojx6-d085b09386.json') 
		firebase_admin.initialize_app(cred)
	print("db set")
	global db
	db = firestore.client()
	
	return db

def add_user(user_id, name):
	print("name: %s; id =%s" % (name, user_id))

	doc = {
		'user-id': user_id,
		'name': name
	}

	# 語法
	# doc_ref = db.collection("集合名稱").document("文件id")
	db = get_db()
	doc_ref = db.collection("user").document(name)

	# doc_ref提供一個set的方法，input必須是dictionary
	doc_ref.set(doc)
	return "user id 新增成功"

def search_user(name):
	name_id = get_user_id(name)
	if(name_id == "fail"):
		return "這個 user 不存在名單中喔~"

	return "有這個 user 喔~"

def get_user_id(name):

	db = get_db()
	#Get Collection
	doc_ref = db.collection('user')
	docs = doc_ref.get()
	for doc in docs:
		if(name in doc.id):
			print(u'{} => {}'.format(doc.id, doc.to_dict()))
			return doc.to_dict()["user-id"]
	return "fail"

def get_user_name(user_id):

	db = get_db()
	#Get Collection
	doc_ref = db.collection('user')
	docs = doc_ref.get()
	for doc in docs:
		data = doc.to_dict()
		if(data["user-id"] == user_id):
			return data["name"]
		
	return "NULL user"

def add_to_sendbox(sender_id, receiver_name, add_title, add_content):
	sender_name = get_user_name(sender_id)
	data = {add_title: add_content}

	path = "user/" + sender_name + "/sendbox/" + receiver_name

	db_document = db.document(path)
	db_document.update(data)
	print("add_to_sendbox success")


def send_mailbox(receiver_name, sender_id, mail_type, content):
	'''
	name: receiver
	sender_id: sender id(if anonymous, clear it)
	mail_type: text, img, voice
	content: text, url, link
	'''
	print("receiver:", receiver_name)
	name_id = get_user_id(receiver_name)
	if(name_id == "fail"):
		return "there is no existed user"

	sender_name = get_user_name(sender_id)
	print("sender-name:", sender_name)

	doc = {
		'sender-name': sender_name,
		'receiver-id': name_id,
		'type': mail_type,
		'content': content,
		'read': False
	}

	# date & time as doc title
	now = str(datetime.today())
	day_stamp = now[:now.index(".")]

	path = "user/" + receiver_name + "/mailbox"

	# 語法
	# doc_ref = db.collection("集合名稱").document("文件id")
	doc_ref = db.collection(path).document(day_stamp)

	# doc_ref提供一個set的方法，input必須是dictionary
	doc_ref.set(doc)
	return "已送進信箱囉~ 我會使命必達的~"

def recv_mailbox(receiver_id):
	print("enter recv_mailbox function")
	db = get_db()
	receiver_name = get_user_name(receiver_id)

	#Get Collection
	path = "user/" + receiver_name + "/mailbox"
	doc_ref = db.collection(path)
	docs = doc_ref.get()
	print("receiver_name:", receiver_name)

	for doc in docs:
		data = doc.to_dict()
		print(u'{} => {}'.format(doc.id, data))
		if(data["read"] == False):
			path += ("/" + str(doc.id))
			print("path:", path)
			db_document = db.document(path)
			revise = {"read": True}
			db_document.update(revise)
			print("update data success")
			if(data["type"] == "img"):
				return data["content"], "img", data["sender-name"]
				#return_text = send_image_url(receiver_id, data["content"])
				#return data["sender-name"], return_text, str(doc.id)
			return data["sender-name"], data["content"], str(doc.id)
	return "empty", "fail", "(date)"

