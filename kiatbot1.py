from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

#from oil import get_prices
import oil

app = Flask(__name__)

line_bot_api = LineBotApi('CBVGGYmWiAq9NNKT9cFzMxfV7gKFu55vX/hGi3SzYmmy8oDk3z6Uft+xgRqu8ywcTWs1WtewsKcHD+q7DAfeSbZVA/QojSYCQbhByTm2HRM6gGfrS2WaEQGM7nyPtt2TeROJYRnHz7AlgUupZoj81AdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('23891fbbf252a6b24a97164613246d30')

# @app.route("/", methods=['GET'])
# def default_action():
  #  return 'Hello'


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


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == "ราคาน้ำมัน":
        #line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.message.text+"คร้าบๆๆ"))

        l = oil.get_prices()
        s = ""
        for p in l:
            s += "%s %.2f บาท\n" % (p[0],p[1])
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=s))
    else:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.message.text+"จ้าๆๆ"))

if __name__ == "__main__":
    app.run()