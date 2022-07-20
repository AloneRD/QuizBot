from dotenv import load_dotenv
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import vk_api as vk
from vk_api.utils import get_random_id
import os
import random
from quiz import get_quiz_question


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


def new_question(event, vk_api, keyboard, questions):
    question_answer = next(questions)
    new_question = question_answer[0]
    answer = question_answer[1]
    vk_api.messages.send(
        peer_id=event.user_id,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message=new_question
    )
    return answer


def handle_solution_attempt(event, vk_api, keyboard, answer):
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


def surrender(event, vk_api, keyboard, answer):
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

    longpoll = VkLongPoll(vk_session)

    questions = get_quiz_question()

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            keyboard = get_keyboard(event, vk_api)
            if event.text == "Начать":
                start(event, vk_api, keyboard)
            elif event.text == "Новый вопрос":
                answer = new_question(event, vk_api, keyboard, questions)
            elif event.text == "Сдаться":
                surrender(event, vk_api, keyboard, answer)
            else:
                handle_solution_attempt(event, vk_api, keyboard, answer)