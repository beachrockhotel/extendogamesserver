from flask import Flask, request, jsonify
from models import db, News

def add_news():
    data = request.json
    if not data or 'title' not in data or 'text' not in data:
        return jsonify({"error": "Заголовок и текст должны быть предоставлены"}), 400

    new_news = News(title=data['title'], text=data['text'], image_url=data.get('image_url'))
    db.session.add(new_news)
    db.session.commit()
    return jsonify(message="Новость добавлена", news_id=new_news.id), 201

def get_news():
    news_items = News.query.all()
    news_data = [{'id': news.id, 'title': news.title, 'text': news.text, 'image_url': news.image_url} for news in news_items]
    return jsonify(news=news_data)
