import logging
from flask import Flask, request, jsonify
from models import db, SupportQuestion, PhoneNumber


def post_support_request():
    data = request.get_json()
    email = data.get('email')
    question = data.get('question')
    name = data.get('name')
    new_question = SupportQuestion(user_email=email, question_text=question, user_name=name)
    db.session.add(new_question)
    db.session.commit()

    return jsonify({"status": "success"}), 200

def get_support_requests():
    try:
        support_questions = SupportQuestion.query.all()
        return jsonify([{"email": sq.user_email, "question": sq.question_text, "name": sq.user_name} for sq in support_questions]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def post_support_phone_number():
    data = request.get_json()
    phone_number = data['phoneNumber']
    email = data['email']
    name = data['name']
    new_phone = PhoneNumber(phone=phone_number, email=email, name=name)
    db.session.add(new_phone)
    db.session.commit()
    return jsonify({"status": "success"}), 200


def get_support_phone():
    try:
        phone_numbers = PhoneNumber.query.all()
        return jsonify([{"phoneNumber": pn.phone, "email": pn.email, "name": pn.name} for pn in phone_numbers]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def clear_support_requests():
    try:
        num_deleted_support_questions = SupportQuestion.query.delete()
        db.session.commit()
        return jsonify({
            "message": "Вопросы поддержки успешно очищены",
            "deleted_support_questions": num_deleted_support_questions
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def clear_phone_numbers():
    try:
        num_deleted_phone_numbers = PhoneNumber.query.delete()
        db.session.commit()
        return jsonify({
            "message": "Номера телефонов успешно очищены",
            "deleted_phone_numbers": num_deleted_phone_numbers
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
