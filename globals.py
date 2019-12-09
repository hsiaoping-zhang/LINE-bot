def initialize(): 
	global db 
	cred = credentials.Certificate('./linebot-helper-firebase-adminsdk-bojx6-d085b09386.json') 
	firebase_admin.initialize_app(cred)
	db = firestore.client()
	print("enter initialize function")