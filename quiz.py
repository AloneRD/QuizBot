import glob
import redis
import os
import re
import json
from dotenv import load_dotenv


def upload_questions_redis(db_redis):
    path_files_questions = glob.glob('quiz-questions/*.txt')
    question_number = 1
    for path_file_questions in path_files_questions:
        with open(path_file_questions, 'r', encoding="KOI8-R") as file:
            file = file.read().split("\n\n")
            for item in file:
                if "Вопрос" in item:
                    question = re.sub(r"Вопрос \d*:", '', item)
                if "Ответ" in item:
                    answer = re.sub(r"Ответ:", '', item)
                    question_answer = json.dumps({
                        'question': question,
                        'answer': answer
                      })
                    db_redis.set(f'question_{question_number}', question_answer)
                    question_number += 1


def main():
    load_dotenv()
    password_redis_db = os.getenv("REDIS_DB")
    db_redis = redis.Redis(host='redis-12655.c299.asia-northeast1-1.gce.cloud.redislabs.com', port=12655, db=0, password=password_redis_db)
    upload_questions_redis(db_redis)


if __name__ =='__main__':
    main()