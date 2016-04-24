import telepot
import time
from elasticsearch import Elasticsearch
import os

time.sleep(1)

TELEGRAM_API_KEY = os.getenv('TELEGRAM_API_KEY')
bot = telepot.Bot(TELEGRAM_API_KEY)

ES_HOST = os.getenv('ES_HOST', default='localhost')
es = Elasticsearch([ES_HOST])
while not es.ping():
    print("Waiting for elasticsearch to launch...")
    time.sleep(1)

action_providers = dict()
states = dict()
chat_handlers = dict()


def action_provider(name):
    def decorator(func):
        action_providers[func.__name__] = func
        return func

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


def handle(msg):
    print(msg)
    if 'text' in msg:
        q = msg['text']
    else:
        bot.sendMessage(msg['chat']['id'], 'Извините, я могу отвечать только на текстовые сообщения.')
    res = es.search(body={"query": {"query_string": {"query": q, "fields": ["question^3", "answer"]}}})
    # print(res)

    if (len(res['hits']['hits']) == 0 or res['hits']['hits'][0]['_score'] < 0.1):
        bot.sendSticker(msg['chat']['id'],
                        'BQADAgADKwAD4mVWBHQ_r1atEEueAg')
        bot.sendMessage(msg['chat']['id'], 'В данный момент я не могу ответить на ваш вопрос. Попробуйте позже.')
    else:
        ques = res['hits']['hits'][0]['_source']['question']
        ans = res['hits']['hits'][0]['_source']['answer']
        score = res['hits']['hits'][0]['_score']
        format_string = "Relevancy:{rel}\nВопрос: {question}\nОтвет: {answer}"
        formatted = format_string.format(rel=score, question=ques, answer=ans)
        bot.sendMessage(msg['chat']['id'], formatted)

print(bot.getMe())
bot.message_loop(handle)
print('Listening ...')
while 1:
    time.sleep(10)
