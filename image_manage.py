import tempfile, os
from linebot import LineBotApi
from imgurpython import ImgurClient

from config import client_id, client_secret, album_id, access_token, refresh_token
from config import line_channel_access_token

from firebase import get_user_name

def upload_image(sender_id, receiver_name, img_id):

    print("enter upload_image function")
    print("img id:", img_id)
    line_bot_api = LineBotApi(str(line_channel_access_token))
    message_content = line_bot_api.get_message_content(str(img_id))
    ext = "jpg"

    with tempfile.NamedTemporaryFile(dir="./img", prefix=ext + '-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '.' + ext
    dist_name = "./img/" + os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)

    sender_name = get_user_name(sender_id)

    try:
        client = ImgurClient(client_id, client_secret, access_token, refresh_token)
        print("client connect success")
        config = {
            'album': album_id,
            'name': sender_name,
            'title': receiver_name,
            'description': 'from LINE bot image'
        }

        path = os.path.join(dist_name)
        path = path.replace("\\", "/")
        print("path:", path)

        url = client.upload_from_path(path, config=config, anon=False)["link"]
        print("return url:", url)
        os.remove(path)
        print("image upload success")
        return url

    except:
        print("error to upload image")
        return "fail"
        