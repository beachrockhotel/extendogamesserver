from flask import request, jsonify
from models import db, Question, Answer

def get_questions():
    questions = Question.query.all()
    results = []
    for question in questions:
        answers = [{'id': answer.id, 'text': answer.text, 'userEmail': answer.user_email} for answer in question.answers]
        results.append({
            'id': question.id,
            'userEmail': question.user_email,
            'text': question.text,
            'answers': answers
        })
    return jsonify(results)


def add_question():
    data = request.get_json()
    if not data or 'userEmail' not in data or 'text' not in data:
        return jsonify({"error": "Недостаточно данных для создания вопроса"}), 400
    new_question = Question(user_email=data['userEmail'], text=data['text'])
    db.session.add(new_question)
    db.session.commit()
    return jsonify(message="Вопрос добавлен"), 201

def add_answer(question_id):
    data = request.get_json()
    if not data or 'text' not in data or 'userEmail' not in data:
        return jsonify({"error": "Недостаточно данных для создания ответа"}), 400
    new_answer = Answer(question_id=question_id, text=data['text'], user_email=data['userEmail'])
    db.session.add(new_answer)
    db.session.commit()
    return jsonify(message="Ответ добавлен"), 201

