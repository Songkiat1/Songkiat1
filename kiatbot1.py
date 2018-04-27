from flask import Flask, request, abort

import errno
import os
import sys
import tempfile

from CarAnalytics import LicencePlate

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    ImageMessage, VideoMessage, AudioMessage, 
)

#from oil import get_prices
import oil

app = Flask(__name__)

last_images_part = ""

line_bot_api = LineBotApi('CBVGGYmWiAq9NNKT9cFzMxfV7gKFu55vX/hGi3SzYmmy8oDk3z6Uft+xgRqu8ywcTWs1WtewsKcHD+q7DAfeSbZVA/QojSYCQbhByTm2HRM6gGfrS2WaEQGM7nyPtt2TeROJYRnHz7AlgUupZoj81AdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('23891fbbf252a6b24a97164613246d30')

# @app.route("/", methods=['GET'])
# def default_action():
  #  return 'Hello'
static_tmp_path = os.path.join(os.path.dirname(__file__), 'KiatBot', 'tmp')
# function for create tmp dir for download content
def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=(ImageMessage, VideoMessage, AudioMessage))
def handle_content_message(event):
    global last_images_part
    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
    elif isinstance(event.message, VideoMessage):
        ext = 'mp4'
    elif isinstance(event.message, AudioMessage):
        ext = 'm4a'
    else:
        return

    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '.' + ext
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)

    last_images_part = dist_path
    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text="เก็บรูป")
                
        ])


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global last_images_part
    if event.message.text == "ราคาน้ำมัน":
        #line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.message.text+"คร้าบๆๆ"))

        l = oil.get_prices()
        s = ""
        for p in l:
            s += "%s %.2f บาท\n" % (p[0],p[1])
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=s))
    elif event.message.text == "วิเคราะห์รูป":
        try:
            if(last_images_part != None):
                lp = LicencePlate()
                result = lp.process(last_images_part)
                s = lp.translate(result)

                line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text=s)
                    ])
            else:
                line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text="กรุณาส่งรูปภาพใหม่")  
                    ])
        except Exception as e:
                line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text="ไม่สามารถประมวลผลรูปภาพ")  
                    ])
    else:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.message.text+"จ้าๆๆ"))

if __name__ == "__main__":
    app.run()