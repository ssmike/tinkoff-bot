providers_list = dict()
user_state = dict()
current_chat_handlers = dict()


def action_provider(name):
    def decorator(func):
        providers_list[func.__name__] = func
        return func
    return decorator

user_context = dict()


def init(chat_id):
    if (chat_id not in user_context):
        user_context[chat_id] = dict()
    if (chat_id not in current_chat_handlers):
        current_chat_handlers[chat_id] = None
        user_state[chat_id] = 0


@action_provider("pay_phone")
def pay_phone(chat_id, text, telegram_message=None, bot=None):
    init(chat_id)
    if (current_chat_handlers[chat_id] is None):
        current_chat_handlers[chat_id] = "pay_phone"
        user_state[chat_id] = 0
    if (user_state[chat_id] == 0):
        user_state[chat_id] = 1
        return "Введите номер телефона"
    if (user_state[chat_id] == 1):
        user_context[chat_id]['phone_number'] = text
        user_state[chat_id] = 2
        return "Введите сумму"
    if (user_state[chat_id] == 2):
        current_chat_handlers[chat_id] = None
        return "Я отправил вам {amount} на телефон {phone_number}".format(
                        amount=text, phone_number=user_context[chat_id]['phone_number'])


@action_provider("get_atms")
def get_atms(chat_id, text, telegram_message=None, bot=None):
    init(chat_id)
    if (current_chat_handlers[chat_id] is None):
        current_chat_handlers[chat_id] = "get_atms"
        user_state[chat_id] = 0
    if (user_state[chat_id] == 0):
        user_state[chat_id] = 1
        return "Отправьте мне свои данные геолокации"
    if (user_state[chat_id] == 1):
        if ('location' in telegram_message):
            longitude = telegram_message['location']['longitude']
            latitude = telegram_message['location']['latitude']
            print(telegram_message)
            current_chat_handlers[chat_id] = None
            bot.sendLocation(chat_id, latitude=latitude, longitude=longitude)
            return "Готово"
        else:
            return "Отправьте свои геолокационные данные (скрепочка снизу справа)"
