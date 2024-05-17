from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)  # URL изображения товара

    def __repr__(self):
        return f'<MenuItem {self.name}>'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(100), nullable=False)
    table_number = db.Column(db.String(20), nullable=True)
    total_price = db.Column(db.Float, nullable=False)
    order_time = db.Column(db.DateTime, default=datetime.utcnow)  # Обратите внимание на default

    items = db.relationship('OrderItem', backref='order', lazy=True)

    def __repr__(self):
        return f'<Order id={self.id}, user_name={self.user_name}>, user_name={self.user_name}>'

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_time_of_order = db.Column(db.Float, nullable=False)

    menu_item = db.relationship('MenuItem', backref='order_items', lazy=True)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=True)
    user_email = db.Column(db.String(100), nullable=False)
    seat_number = db.Column(db.Integer, nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Reservation seat_number={self.seat_number} date={self.date} time={self.time}>'

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<News {self.title}>'

class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    discipline = db.Column(db.String(255), nullable=False)
    prize_pool = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Tournament {self.title}>'

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(255), nullable=False)
    representative_name = db.Column(db.String(255), nullable=False)
    representative_email = db.Column(db.String(255), nullable=False)
    members = db.Column(db.Text, nullable=False)
    tournament_name = db.Column(db.String(255), nullable=False)
    discipline = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Team {self.team_name}>'

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), nullable=False)  # Changing from user_name to user_email
    text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Review {self.user_email} - {self.rating}>'

class SupportQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), nullable=False)
    question_text = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<SupportQuestion {self.user_email}>'

class PhoneNumber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(15), nullable=False)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    answers = db.relationship('Answer', backref='question', lazy=True)

    def __repr__(self):
        return f'<Question {self.user_email} - {self.text}>'

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    user_email = db.Column(db.String(100), nullable=False)  # Добавленный столбец
    text = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Answer {self.user_email} - {self.text}>'