import os
from functools import partial
from typing import NoReturn
from dotenv import load_dotenv

import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters


def main():
    load_dotenv()
    tg_token = os.getenv("TG_TOKEN")

    updater = Updater(token=tg_token)
    dispacher = updater.dispatcher

    custom_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Мой счет']]
    menu_keyboard = telegram.ReplyKeyboardMarkup(custom_keyboard)
    questions = get_quiz_question()
    dispacher.add_handler(CommandHandler("start", partial(start_callback, keyboard=menu_keyboard)))
    dispacher.add_handler(MessageHandler(Filters.text, partial(responds_to_user, question=questions)))

    updater.start_polling()


def start_callback(update, context, keyboard) -> NoReturn:
    update.message.reply_text("Здравствуйте", reply_markup=keyboard)


def responds_to_user(update, context, question) -> NoReturn:
    message_text = update.message.text
    if message_text == "Новый вопрос":
        question_answer = next(question)
        new_question = question_answer[0]
    update.message.reply_text(new_question)


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
