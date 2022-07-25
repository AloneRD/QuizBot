import os
from functools import partial
from typing import NoReturn
from dotenv import load_dotenv

import telegram
import redis
import json
import re
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import ConversationHandler


def start(update, _) -> NoReturn:
    custom_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Мой счет']]
    menu_keyboard = telegram.ReplyKeyboardMarkup(custom_keyboard)

    update.message.reply_text("Здравствуйте", reply_markup=menu_keyboard)
    return 'NEW_QUESTION'


def handle_new_question_request(update, context, db_redis) -> NoReturn:
    chat_id = update.message.chat.id
    user_in_redis = db_redis.get(f'user_tg_{chat_id}')
    if user_in_redis:
        last_asked_question = json.loads(user_in_redis)['last_asked_question']
        last_question_number = int(re.match(r'question_(\d)', last_asked_question).group(1))
        next_question = f"question_{last_question_number+1}"
        question_answer = json.loads(db_redis.get(next_question))
        if not question_answer:
            question_answer = json.loads(db_redis.get("question_1"))
            db_redis.set(f'user_tg_{chat_id}', json.dumps({"last_asked_question": "question_1"}))
        else:
            db_redis.set(f'user_tg_{chat_id}', json.dumps({"last_asked_question": next_question}))       
    else:
        db_redis.set(f'user_tg_{chat_id}', json.dumps({"last_asked_question": "question_1"}))
        question_answer = json.loads(db_redis.get("question_1"))
    question = question_answer['question']
    answer = question_answer['answer']
    context.user_data['answer'] = answer
    update.message.reply_text(question)
    return 'ANSWER'


def handle_solution_attempt(update, context):
    message_text = update.message.text
    correct_answer = context.user_data['answer']
    if message_text.lower() in correct_answer.lower():
        update.message.reply_text("Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос")
        return 'NEW_QUESTION'
    elif message_text == "Сдаться":
        update.message.reply_text(context.user_data['answer'])
        return 'NEW_QUESTION'
    else:
        update.message.reply_text("Неправильно… Попробуешь ещё раз?")


def cancel(update, _):
    update.message.reply_text('Будет скучно - пиши.', reply_markup=telegram.ReplyKeyboardRemove())
    return ConversationHandler.END


def main():
    load_dotenv()
    tg_token = os.getenv("TG_TOKEN")
    password_redis_db = os.getenv("REDIS_DB")
    db_redis = redis.Redis(host='redis-12655.c299.asia-northeast1-1.gce.cloud.redislabs.com', port=12655, db=0, password=password_redis_db)

    updater = Updater(token=tg_token)
    dispacher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            'NEW_QUESTION': [MessageHandler(
                Filters.regex('Новый вопрос|start'),
                partial(handle_new_question_request, db_redis=db_redis))],
            'ANSWER': [MessageHandler(
                Filters.text,
                handle_solution_attempt)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    dispacher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
