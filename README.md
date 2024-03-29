# LINE bot
[ 計算理論 ] 聊天機器人 - 小小幫手

## 功能概要說明
此機器人主要任務類似於傳情，透過資料庫 firebase 儲存各用戶收到的訊息們，而訊息並不會即時的被對方得知，
傳情者可以選擇匿名方式，更甚是使用**未來信**功能，讓你與對方之間的訊息在時間裡沉澱、發酵。

## FSM
![](https://i.imgur.com/yF5nfFJ.jpg)

## 使用 / 程式流程
### 新增使用者
```
新增 名稱
```
從 `event.source.user_id` 得知使用者的 id ，並透過 Firebase 資料庫創造使用者信箱。
<hr/>

### 搜尋使用者
```
搜尋 名稱
```
搜尋 user 名單當中是否有該位使用者。
<hr/>


### 寄信
1. 我要送信
2. 收件者名稱
3. 訊息形式 ex: 圖片 / 文字
4. 撰寫訊息
5. 署名名稱
6. 收件日期
```
# 我要送信

> 你想要送給誰?
# 管理員

> 形式是什麼? 文字(text) / 圖片(img)
# 文字

> 開始寫訊息給我吧~
# 嗨嗨你好，今年臺南的冬天好冷，但還是祝你聖誕節快樂

> [文字訊息]已接收
> 署名： (如果想匿名直接輸入匿名)
# 想冬眠的小孩

> 日期模式(無：隨寄隨收 / 20XX XX XX：未來信)
> - - -
> 如果日期小於今天，一樣視同「無」
# 2019 12 25 (未來信)

> 已送進信箱了~ 我會使命必達的~
```
<hr/>

- 使用 linebot 當中 ImageSendMessage 功能傳送圖片
- 使用者傳給 linebot 圖片需要透過 id 進行 get_message_content 抓取圖片， 之後再上傳至 Imgur 轉換成 url 存回資料庫，以利於往後讀取方便性。

### 收信
1. 收信
2. 是否刪除此則訊息? (是 / 否)

```
# 收信
> 來自 想冬眠的小孩 的訊息
> - - -
> 嗨嗨你好，今年臺南的冬天好冷，但還是祝你聖誕節快樂
> - - - 
> 時間：2019-12-10 21:57:39

> 是否刪除這則訊息(是 / 否)
# 是

> 已刪除
```
<hr/>
連結 Firebase 資料庫，刪除該訊息。


### 空氣品質
```
空氣品質 縣市 / 測站名稱
```
[空氣品質爬蟲網站](http://opendata2.epa.gov.tw/AQI.json)
使用 `requests` 及 `json` 套件對於網頁資訊進行爬取。

### 休息 / 甦醒
透過 `小小幫手休息` 能讓機器人暫時不回應；`小小幫手起床` 讓機器人重新恢復功能。
