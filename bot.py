import telepot
import time
from elasticsearch import Elasticsearch
import os
import re
from flask import Flask, request
import sys
from importance import *

hello_words = ['привет', 'приветики', 'здарова', 'приветствую', 'здравствуйте', 'приффки',
               'хай', 'хей', 'добрый', 'доброе', 'доброго']
bye_words = ['спасибо', 'ладно', 'ок', 'доброго', 'пока', 'свидания', 'встреч', 'спокойной',
             'наилучшего', 'хорошо', 'отлично', 'спс']

hello_w = 'Здравствуйте. '
bye_w = ' Если ко мне вопросов больше нет, всего доброго, до свидания.'

app = Flask(__name__)
vects, vec_len = {}, 100
with open(sys.argv[1]) as f:
    vects, vec_len = read_vectors(f.readlines())

TELEGRAM_API_KEY = os.getenv('TELEGRAM_API_KEY')
bot = telepot.Bot(TELEGRAM_API_KEY)

ES_HOST = os.getenv('ES_HOST', default='localhost')
es = Elasticsearch([ES_HOST])
good = False
while not good:
    good = False
    time.sleep(1)
    try:
        while not es.ping():
            print("Waiting for elasticsearch to launch...")
            time.sleep(1)
        good = True
    except:
        good = False

action_providers = dict()
states = dict()
chat_handlers = dict()


def action_provider(name):
    def decorator(func):
        action_providers[func.__name__] = func
        return func
    return decorator

phone_numbers = dict()


@action_provider("pay_phone")
def pay_phone(msg):
    chat_id = msg['chat']['id']
    if (chat_id not in states):
        chat_handlers[chat_id] = "pay_phone"
        states[chat_id] = 0
    if (states[chat_id] == 0):
        bot.sendMessage(chat_id, "Введите номер телефона")
        states[chat_id] = 1
    if (states[chat_id] == 1):
        phone_numbers[chat_id] = msg['text']
        bot.sendMessage(chat_id, "Введите сумму")
        states[chat_id] = 2
    if (states[chat_id] == 2):
        bot.sendMessage(chat_id, "Я отправил вам {amount} на телефон {phone_number}",
                        amount=msg['text'], phone_number=phone_numbers[chat_id])


def answer_message(chat_id, text, is_in_telegram_chat=True):
    vq = re.split("[\'\"\:\-\.!?\s=\(\)]+", text)
    text = " ".join([x.lower() for x in vq])
    hello = False
    bye = False

    for h in hello_words:
        if h in vq:
            hello = True

    for b in bye_words:
        if b in vq:
            bye = True
    print(">>>>>>", trim(text, vects, vec_len))
    print(">>>>>>", importance(text, vects, vec_len))
    res = es.search(body={"query": {"query_string": {"query": trim(text, vects, vec_len), "fields": ["question^3", "answer"]}}})

    if (len(res['hits']['hits']) == 0 or res['hits']['hits'][0]['_score'] < 0.1):
        if is_in_telegram_chat:
            bot.sendSticker(chat_id,
                            'BQADAgADKwAD4mVWBHQ_r1atEEueAg')
        return 'В данный момент я не могу ответить на ваш вопрос. Попробуйте позже.'
    else:
        ques = res['hits']['hits'][0]['_source']['question']
        ans = res['hits']['hits'][0]['_source']['answer']

        if hello:
            ans = hello_w + ans
        if bye:
            ans += bye_w

        score = res['hits']['hits'][0]['_score']
        format_string = "Relevancy:{rel}\nВопрос: {question}\nОтвет: {answer}"
        formatted = format_string.format(rel=score, question=ques, answer=ans)
        return formatted


def handle(msg):
    if 'text' not in msg:
        bot.sendSticker(msg['chat']['id'],
                        'BQADAgADKwAD4mVWBHQ_r1atEEueAg')
        bot.sendMessage(msg['chat']['id'],
                        'Извините, я могу отвечать только на текстовые сообщения.')
        return
    chat_id = msg['chat']['id']
    text = msg['text']
    ans = answer_message(chat_id, text)
    bot.sendMessage(chat_id, ans)

print(bot.getMe())
bot.message_loop(handle)


@app.route('/', methods=['POST'])
def handleHTTPRequest():
    print(request.get_data().decode("utf-8"))
    return answer_message(0, request.get_data().decode("utf-8") , is_in_telegram_chat=False)

print('Listening ...')
app.run(host='0.0.0.0', port=8000)
