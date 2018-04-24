#!/usr/bin/env python
# coding: utf-8

from gae_http_client import RequestsHttpClient

from google.appengine.api import taskqueue

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

import datetime

import config

app = Flask(__name__)

line_bot_api = LineBotApi(config.CHANNEL_ACCESS_TOKEN, http_client=RequestsHttpClient)
handler = WebhookHandler(config.CHANNEL_SECRET)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # Task Queue Add
    taskqueue.add(url='/worker',
                  params={'body': body,
                          'signature': signature},
                  method="POST")

    return 'OK'

@app.route("/worker", methods=['POST'])
def worker():
    body = request.form.get('body')
    signature = request.form.get('signature')

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    keyword=unicode(event.message.text, "utf-8")
    if keyword == "平軒" or keyword == "軒哥" or keyword == "蕭平軒":

        now=datetime.datetime.now()

        hours=now.hours
        if hours > 9 and hours < 12:
            foodTime=datetime.datetime(now.year, now.month, now.day, 12, 00)
            temp=foodTime-now
            timeList=str(temp).split(".")[0].split(":")
            result='報告軒哥，離午餐時間還有 ' + timeList[0] + ' 小時 ' + timeList[1] + ' 分又 ' + timeList[2] + ' 秒'
        elif hours >= 12 and hours < 13:
            result='報告軒哥，吃晚午餐該睡囉～'
        elif hours >= 13 and hours < 18:
            foodTime=datetime.datetime(now.year, now.month, now.day, 18, 00)
            temp=foodTime-now
            timeList=str(temp).split(".")[0].split(":")
            result='報告軒哥，離晚餐時間還有 ' + timeList[0] + ' 小時 ' + timeList[1] + ' 分又 ' + timeList[2] + ' 秒'
        elif hours >=18 and hours < 19:
            result='報告軒哥，吃完晚餐該回家陪女兒囉～'
        elif hours >= 19 and hours < 23:
            result='噓～軒哥在家很安靜的'
        elif hours >= 23 or (hours >= 0 and hours < 7):
            result='幹，快睡'
        elif hours >=7 and hours < 9:
            result='別打擾軒哥吃早餐'
        else:
            result='軒哥好！'

        result='軒哥好！'

    else:
        result='錯囉～'

    line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))


if __name__ == "__main__":
    app.run()
