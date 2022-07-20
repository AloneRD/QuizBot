# Quiz Bot

Данный бот предназначен для проведения викторин
## Запуск бота локально
Для запуска бота на вашем сервере необходимо выполнить следующие действия:

1. Cоздать бота в Телеграмм  [см.тут](https://core.telegram.org/bots).
2. Инициализировать с вашим ботом чат.
3. Склонировать себе файлы репозитория выполнив команду **https://github.com/AloneRD/QuizBot.git**.
4. Установить необходимы зависимости **pip install -r requirements.txt**.
5. В директории с проектом создать файл **.env** со следующим содержимом:
 ```
    TG_TOKEN=5516774215:AAGLNELFcE7RHWcW2dJpBxEEuLB3C4E7cVM
    VK_TOKEN=vk1.a.9-U8Fmli6F6Yvp3Oist-vlF2Ia_J7_0goKh-TmFPHjIyhT37P8TK4Oj14rtsag0kgFe4PaF1J6ay7I
    REDIS_DB=AS0rbPRkOaJA
 ```
   - **VK_TOKEN** токен к вашему ВК боту
   - **TG_TOKEN** токен к вашему телеграмм боту
   - **REDIS_DB** ключ доступа к Redis
6. запустить бота **.\tg_bot.py** или **.\vk_bot.py**
7. Вопросы генерируются из txt файлов в директории  quiz-questions
8. Пример файла с вопросами 
 ```
    Вопрос 1:
    С одним советским туристом в Марселе произошел такой случай. Спустившись
    из своего номера на первый этаж, он вспомнил, что забыл закрутить кран в
    ванной. Когда он поднялся, вода уже затопила комнату. Он вызвал
    горничную, та попросила его обождать внизу. В страхе он ожидал расплаты
    за свою оплошность. Но администрация его не ругала, а, напротив,
    извинилась сама перед ним. За что?

    Ответ:
    За то, что не объяснила ему правила пользования кранами.

    Автор:
    Максим Поташев


    Вопрос 2:
    В своем первоначально узком значении это слово произошло от французского
    глагола, означающего "бить". Сейчас же оно может означать любое
    объединение в систему нескольких однотипных элементов. Назовите это
    слово.

    Ответ:
    Батарея (от battre).

    Источник:
    СЭС
 ```

