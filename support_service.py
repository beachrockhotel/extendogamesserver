import logging
from flask import Flask, request, jsonify
from models import db, SupportQuestion, PhoneNumber


def post_support_request():
    data = request.get_json()
    email = data.get('email')
    question = data.get('question')

    # Создание нового объекта SupportQuestion
    new_question = SupportQuestion(user_email=email, question_text=question)
    db.session.add(new_question)
    db.session.commit()

    return jsonify({"status": "success"}), 200

def get_support_requests():
    try:
        support_questions = SupportQuestion.query.all()
        return jsonify([{"email": sq.user_email, "question": sq.question_text} for sq in support_questions]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def post_support_phone_number():
    data = request.get_json()
    phone_number = data['phoneNumber']
    new_phone = PhoneNumber(phone=phone_number)
    db.session.add(new_phone)
    db.session.commit()
    return jsonify({"status": "success"}), 200

def get_support_phone():
    try:
        phone_numbers = PhoneNumber.query.all()
        return jsonify([{"phoneNumber": pn.phone} for pn in phone_numbers]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
