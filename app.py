import os
from functools import partial
from typing import NoReturn
from dotenv import load_dotenv

import telegram
import redis
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import ConversationHandler


def main():
    load_dotenv()
    tg_token = os.getenv("TG_TOKEN")
    password_redis_db = os.getenv("REDIS_DB")
    db_redis = redis.Redis(host='redis-12655.c299.asia-northeast1-1.gce.cloud.redislabs.com', port=12655, db=0, password=password_redis_db)
    questions = get_quiz_question()

    updater = Updater(token=tg_token)
    dispacher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            'NEW_QUESTION': [MessageHandler(
                Filters.text,
                partial(handle_new_question_request, question=questions, db_redis=db_redis))],
            'ANSWER': [MessageHandler(
                Filters.text,
                handle_solution_attempt)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    dispacher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


def start(update, _) -> NoReturn:
    custom_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Мой счет']]
    menu_keyboard = telegram.ReplyKeyboardMarkup(custom_keyboard)

    update.message.reply_text("Здравствуйте", reply_markup=menu_keyboard)
    return 'NEW_QUESTION'


def handle_new_question_request(update, context, question, db_redis) -> NoReturn:
    message_text = update.message.text
    chat_id = update.message.chat.id
    if message_text == "Новый вопрос":
        question_answer = next(question)
        new_question = question_answer[0]
        context.user_data['answer'] = question_answer[1]
        db_redis.set(chat_id, new_question)
        update.message.reply_text(db_redis.get(chat_id).decode())
    return 'ANSWER'


def handle_solution_attempt(update, context):
    message_text = update.message.text
    correct_answer = context.user_data['answer']
    if message_text.lower() in correct_answer.lower():
        update.message.reply_text("Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос")
        return 'NEW_QUESTION'
    else:
        update.message.reply_text("Неправильно… Попробуешь ещё раз?")


def cancel(update, _):
    update.message.reply_text('Будет скучно - пиши.', reply_markup=telegram.ReplyKeyboardRemove())
    return ConversationHandler.END


def get_quiz_question():
    with open('quiz-questions/1vs1200.txt', 'r', encoding="KOI8-R") as file:
        file = file.read().split("\n\n")
        questions_answers = {}
        for item in file:
            if "Вопрос" in item:
                question = item.split(":")
            if "Ответ" in item:
                answer = item.split(":")
            try:
                questions_answers[question[1]] = answer[1]
            except:
                pass
        for question, answer in questions_answers.items():
            yield (question, answer)


if __name__ == '__main__':
    main()
