import flask
from flask import request
import os
from bot import Bot, QuoteBot, ImageProcessingBot
import subprocess

app = flask.Flask(__name__)

TELEGRAM_TOKEN = ''
TELEGRAM_APP_URL = 'https://t.me/Ronn4_bot'


@app.route('/', methods=['GET'])
def index():
    return 'Ok'


@app.route(f'/{TELEGRAM_TOKEN}/', methods=['POST'])
def webhook():
    req = request.get_json()
    if 'message' in req:
        QuoteBot.handle_message(req['message'])
    return 'Ok'


if __name__ == "__main__":
    QuoteBot = ImageProcessingBot(TELEGRAM_TOKEN, TELEGRAM_APP_URL)

    app.run(host='0.0.0.0', port=8443)
