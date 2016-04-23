import telepot
import time
from elasticsearch import Elasticsearch
import os

TELEGRAM_API_KEY = os.getenv('TELEGRAM_API_KEY')
ES_HOST = os.getenv('ES_HOST', default='localhost')
es = Elasticsearch([ES_HOST])
bot = telepot.Bot(TELEGRAM_API_KEY)


def handle(msg):
    if 'text' in msg:
        q = msg['text']
    else:
        bot.sendMessage(msg['chat']['id'],
                        'Извините, я могу отвечать только на текстовые сообщения.')
    res = es.search(body={"query": {"query_string": {"query": q, "fields": ["question"] }}})
    # print(res)
    if (len(res['hits']['hits']) == 0 or res['hits']['hits'][0]['_score'] < 0.3):
        bot.sendMessage(msg['chat']['id'],
                        'В данный момент я не могу ответить на ваш вопрос. Попробуйте позднее.')
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
