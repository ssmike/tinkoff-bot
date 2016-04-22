import telepot
import time
from elasticsearch import Elasticsearch

es = Elasticsearch()


bot = telepot.Bot('204599736:AAGGV6WCHH21mRiYD_MxncwyBR7mIM9T96M')


def handle(msg):
    q = msg['text']
    res = es.search(body={"query": {"query_string": {"query": q}}})
    # print(res)
    if (len(res['hits']['hits']) == 0 or res['hits']['hits'][0]['_score'] < 0.3):
        bot.sendMessage(msg['chat']['id'], 'я хз')
    else:
        ques = res['hits']['hits'][0]['_source']['question']
        ans = res['hits']['hits'][0]['_source']['answer']
        score = res['hits']['hits'][0]['_score']
        formatted = "Relevancy:{rel}\nВопрос: {question}\nОтвет: {answer}".format(rel=score, question=ques, answer=ans)
        bot.sendMessage(msg['chat']['id'], formatted)

print(bot.getMe())
bot.message_loop(handle)
print('Listening ...')
while 1:
    time.sleep(10)
