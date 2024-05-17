from flask import request, jsonify
from models import db, Review

def get_reviews():
    reviews = Review.query.all()
    return jsonify([{'userEmail': review.user_email, 'text': review.text, 'rating': review.rating} for review in reviews])


def add_review():
    data = request.get_json()
    if not data or 'userEmail' not in data or 'text' not in data or 'rating' not in data:
        return jsonify({"error": "Недостаточно данных для создания отзыва"}), 400
    new_review = Review(user_email=data['userEmail'], text=data['text'], rating=data['rating'])
    db.session.add(new_review)
    db.session.commit()
    return jsonify(message="Отзыв добавлен"), 201

