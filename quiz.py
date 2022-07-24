import glob


def get_quiz_question():
    path_files_questions = glob.glob('quiz-questions/*.txt')
    for path_file_questions in path_files_questions:
        with open(path_file_questions, 'r', encoding="KOI8-R") as file:
            file = file.read().split("\n\n")
            questions_answers = {}
            for item in file:
                if "Вопрос" in item:
                    question = item.split(":")
                if "Ответ" in item:
                    answer = item.split(":")
                try:
                    questions_answers[question[1]] = answer[1]
                except UnboundLocalError:
                    pass
            for question, answer in questions_answers.items():
                yield (question, answer)
