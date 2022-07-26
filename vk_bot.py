from dotenv import load_dotenv
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import vk_api as vk
from vk_api.utils import get_random_id
import os
import redis
import json
import re


def get_keyboard(event, vk_api):
    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()  # Переход на вторую строку
    keyboard.add_button('Мой счет', color=VkKeyboardColor.SECONDARY)

    return keyboard


def start(event, vk_api, keyboard):
    vk_api.messages.send(
        peer_id=event.user_id,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message='Здравствуйте'
    )


def new_question(event, vk_api, keyboard, user_in_redis, user_id):
    if user_in_redis:
        last_asked_question = json.loads(user_in_redis)['last_asked_question']
        last_question_number = int(re.match(r'question_(\d)', last_asked_question).group(1))
        next_question = f"question_{last_question_number+1}"
        question_answer = json.loads(db_redis.get(next_question))
        if not question_answer:
            question_answer = json.loads(db_redis.get("question_1"))
            db_redis.set(f'user_vk_{user_id}', json.dumps({"last_asked_question": "question_1"}))
        else:
            db_redis.set(f'user_vk_{user_id}', json.dumps({"last_asked_question": next_question}))       
    else:
        db_redis.set(f'user_vk_{user_id}', json.dumps({"last_asked_question": "question_1"}))
        question_answer = json.loads(db_redis.get("question_1"))
    question = question_answer['question']

    vk_api.messages.send(
        peer_id=event.user_id,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message=question
    )


def handle_solution_attempt(event, vk_api, keyboard, user_in_redis, user_id):
    last_asked_question = json.loads(user_in_redis)['last_asked_question']
    question_answer = json.loads(db_redis.get(last_asked_question))
    answer = question_answer['answer']

    if event.text in answer:
        message = "Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос"
    else:
        message = "Неправильно… Попробуешь ещё раз?"
    vk_api.messages.send(
        peer_id=event.user_id,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message=message
    )


def surrender(event, vk_api, keyboard, user_in_redis, user_id):
    last_asked_question = json.loads(user_in_redis)['last_asked_question']
    question_answer = json.loads(db_redis.get(last_asked_question))
    answer = question_answer['answer']

    vk_api.messages.send(
        peer_id=event.user_id,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message=answer
    )


if __name__ == "__main__":
    load_dotenv()
    vk_token = os.getenv("VK_TOKEN")
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    password_redis_db = os.getenv("REDIS_DB")
    db_redis = redis.Redis(host='redis-12655.c299.asia-northeast1-1.gce.cloud.redislabs.com', port=12655, db=0, password=password_redis_db)

    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():

        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            keyboard = get_keyboard(event, vk_api)

            if event.text == "Начать":
                start(event, vk_api, keyboard)
                user_id = event.user_id
                user_in_redis = db_redis.get(f'user_vk_{user_id}')
            elif event.text == "Новый вопрос":
                new_question(event, vk_api, keyboard, user_in_redis, user_id)
            elif event.text == "Сдаться":
                surrender(event, vk_api, keyboard, user_in_redis, user_id)
            else:
                handle_solution_attempt(event, vk_api, keyboard, user_in_redis, user_id)
