import telepot
import time
from elasticsearch import Elasticsearch
import os
import re
from flask import Flask, request
import action_providers

hello_words = ['привет', 'приветики', 'здарова', 'приветствую', 'здравствуйте', 'приффки',
               'хай', 'хей', 'добрый', 'доброе', 'доброго']
bye_words = ['спасибо', 'ладно', 'ок', 'доброго', 'пока', 'свидания', 'встреч', 'спокойной',
             'наилучшего', 'хорошо', 'отлично', 'спс']

hello_w = 'Здравствуйте. '
bye_w = ' Если ко мне вопросов больше нет, всего доброго, до свидания.'

app = Flask(__name__)


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


def answer_message(chat_id, text, telegram_message=None):
    print(action_providers.current_chat_handlers)
    print(chat_id)
    if (chat_id in action_providers.current_chat_handlers and
            action_providers.current_chat_handlers[chat_id] is not None):
        provider_name = action_providers.current_chat_handlers[chat_id]
        provider_func = action_providers.providers_list[provider_name]
        if telegram_message:
            message = provider_func(chat_id, text, telegram_message, bot)
        else:
            message = provider_func(chat_id, text)
        return message
    if text in action_providers.providers_list:
        provider_name = text
        provider_func = action_providers.providers_list[provider_name]
        if telegram_message:
            message = provider_func(chat_id, text, telegram_message, bot)
        else:
            message = provider_func(chat_id, text)
        return message

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

    res = es.search(body={"query": {"query_string": {"query": text, "fields": ["question^3", "answer"]}}})

    if (len(res['hits']['hits']) == 0 or res['hits']['hits'][0]['_score'] < 0.1):
        if telegram_message is not None:
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
    chat_id = msg['chat']['id']
    currently_handled_by_provider = (chat_id in action_providers.current_chat_handlers and
                                     action_providers.current_chat_handlers[chat_id] is not None)
    if 'text' not in msg and not currently_handled_by_provider:
        bot.sendSticker(msg['chat']['id'],
                        'BQADAgADKwAD4mVWBHQ_r1atEEueAg')
        bot.sendMessage(msg['chat']['id'],
                        'Извините, я могу отвечать только на текстовые сообщения.')
        return

    if ('text' in msg):
        text = msg['text']
    else:
        text = None
    ans = answer_message(chat_id, text, msg)
    bot.sendMessage(chat_id, ans)

print(bot.getMe())
bot.message_loop(handle)


@app.route('/', methods=['POST'])
def handleHTTPRequest():
    return answer_message(0, request.data)
    print(request.get_data().decode("utf-8"))
    return answer_message(0, request.get_data().decode("utf-8"), is_in_telegram_chat=False)

print('Listening ...')
app.run(host='0.0.0.0', port=8000)
