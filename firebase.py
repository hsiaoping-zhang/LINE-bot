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

def delete_mail(user_id, title):
	
	user_name = get_user_name(user_id)
	db = get_db()
	print("user name:", user_name)
	print("title:", title)
	path = "user/" + user_name + "/mailbox/" + title
	doc_ref = db.document(path);
	doc_ref.delete()
	print("mailbox delete success")


def send_mailbox(receiver_name, sender_id, mail_type, content, name_mode, date_mode):
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
	# print("sender-name:", sender_name)

	# 判斷日期
	if(date_mode == "無"):
		date_time = datetime.today()
	else:
		date_time = datetime.strptime(date_mode, "%Y %m %d")


	doc = {
		'sender-name': name_mode,
		'receiver-id': name_id,
		'type': mail_type,
		'content': content,
		'date': date_time,
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
	current_time = datetime.today()
	print("current time:", current_time)

	for doc in docs:
		data = doc.to_dict()
		string = str(data["date"])
		string = string[:string.index(" ")]
		print(string)
		date_time = datetime.strptime(string, "%Y-%m-%d")
		# print("next:", date["date"])
		if(data["read"] == False and (date_time <= current_time)):
			path += ("/" + str(doc.id))
			db_document = db.document(path)
			revise = {"read": True}
			db_document.update(revise)
			if(data["type"] == "img"):
				return data["content"], "img", str(doc.id)
			return data["sender-name"], data["content"], str(doc.id)
	return "empty", "fail", "(date)"

def get_mailbox_info(user_name, item, value):

	db = get_db()
	receiver_name = get_user_name(receiver_id)

	#Get Collection
	path = "user/" + user_name + "/mailbox"
	doc_ref = db.collection(path)
	docs = doc_ref.get()
	mail_content = ""

	for doc in docs:
		data = doc.to_dict()
		try:
			if(data["read"] == False):
				mail_content += (data["date"] + " | " + data["sender_name"] + "\n")
		except:
			pass

	print("scan complete")
	return mail_content