# -*- encoding: utf8-*-
'''
Parse weather data to response user.

website: https://www.cwb.gov.tw/V8/C/W/W50_index.html
'''
import re
import time
import json
import requests
import warnings
#from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning

url = "http://opendata2.epa.gov.tw/AQI.json"
#url = "https://www.cwb.gov.tw/V7/observe/radar/"
def get_air_quaility(county):

	warnings.simplefilter('ignore',InsecureRequestWarning)
	requests.get(url, verify = False)

	# send request to website and get the html information
	res = requests.get(url, verify = False)
	res.encoding = 'utf-8'
	soup = res.text
	#soup = BeautifulSoup(res.text, "html.parser")

	result = json.loads(str(soup))

	flag = False
	search = "SiteName"
	if("市" in county or "縣" in county):
		search = "County"

	return_string = "搜尋 : " + county + "\n發布時間 : " + result[0]["PublishTime"] + "\n-\n"
	for item in result:
		if(county in item[search]):
			flag = True
			return_string += (item["SiteName"] + " " + item["AQI"] + " " + item["Status"] + "\n")
	
	if(flag == False and search == "SiteName"):
		return_string = "County : " + county + " 找不到測站資料"
	elif(flag == False and search == "County"):
		return_string = "County : " + county + " 找不到該縣(市)資料"

	return return_string

def get_weather(county):
	text = get_air_quaility(county)
	text = text.strip("\n")
	
	return text