from flask import Flask, render_template, request, jsonify
from models import db, Order, Reservation, OrderItem, SupportQuestion, PhoneNumber
import os
from menu_service import add_menu_item, get_menu, make_order, get_orders, get_user_orders, \
    calculate_food_order_statistics
from news_service import get_news, add_news
from reservation_service import reserve_seat, get_reservations, check_availability, cancel_reservation, \
    get_user_reservations, calculate_reservation_statistics
import logging
from support_service import post_support_request, get_support_requests, post_support_phone_number, get_support_phone, \
    clear_support_requests, clear_phone_numbers
from tournament_service import get_tournaments, add_tournament, add_register_team, get_teams
from review_service import get_reviews, add_review
import firebase_admin
from firebase_admin import messaging, credentials
from question_service import get_questions, add_question, add_answer

app = Flask(__name__)

cred = credentials.Certificate('extendogames-bff67-firebase-adminsdk-7ebiu-337f3f092f.json')
firebase_admin.initialize_app(cred)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://dima:123@localhost/club')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

is_db_initialized = False

with app.app_context():
    db.create_all()

logging.basicConfig(level=logging.DEBUG)

@app.before_request
def create_tables():
    global is_db_initialized
    if not is_db_initialized:
        db.create_all()
        is_db_initialized = True

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/menu', methods=['POST'])
def add_menu_endpoint():
    return add_menu_item()

@app.route('/menu', methods=['GET'])
def get_menu_endpoint():
    return get_menu()

@app.route('/order', methods=['POST'])
def order_endpoint():
    return make_order()

@app.route('/orders', methods=['GET'])
def orders_endpoint():
    return get_orders()

@app.route('/reserve', methods=['POST'])
def reserve():
    return reserve_seat()

@app.route('/reservations', methods=['GET'])
def reservations():
    return get_reservations()

@app.route('/user_reservations', methods=['GET'])
def user_reservations():
    return get_user_reservations()

@app.route('/check_availability', methods=['POST'])
def availability():
    return check_availability()

@app.route('/cancel_reservation/<int:reservation_id>', methods=['DELETE'])
def cancel(reservation_id):
    return cancel_reservation(reservation_id)

@app.route('/post_news', methods=['POST'])
def post_news():
    return add_news()

@app.route('/news', methods=['GET'])
def news():
    return get_news()

@app.route('/tournaments', methods=['GET'])
def tournaments():
    return get_tournaments()

@app.route('/post_tournament', methods=['POST'])
def post_tournament():
    return add_tournament()

@app.route('/register_team', methods=['POST'])
def register_team():
    return add_register_team()

@app.route('/teams', methods=['GET'])
def teams():
    return get_teams()

@app.route('/reviews', methods=['GET'])
def reviews():
    return get_reviews()

@app.route('/reviews', methods=['POST'])
def create_review():
    return add_review()

@app.route('/user_orders', methods=['GET'])
def user_orders():
    user_email = request.args.get('email')
    if not user_email:
        return jsonify({"error": "Email parameter is required"}), 400

    return get_user_orders(user_email)

@app.route('/support', methods=['POST'])
def support_request_email():
    return post_support_request()

@app.route('/support_email', methods=['GET'])
def support_request():
    return get_support_requests()

@app.route('/support_phone', methods=['POST'])
def support_request_phone():
    return post_support_phone_number()

@app.route('/support_phone_numbers', methods=['GET'])
def support_phone_numbers():
    return get_support_phone()

@app.route('/questions', methods=['GET'])
def questions():
    return get_questions()

@app.route('/questions', methods=['POST'])
def create_question():
    return add_question()

@app.route('/questions/<int:question_id>/answers', methods=['POST'])
def create_answer(question_id):
    return add_answer(question_id)

@app.route('/reservation_statistics', methods=['GET'])
def reservation_statistics():
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')

    if not from_date or not to_date:
        return jsonify({"error": "from_date and to_date parameters are required"}), 400

    statistics = calculate_reservation_statistics(from_date, to_date)
    return jsonify(statistics), 200

@app.route('/food_order_statistics', methods=['GET'])
def food_order_statistics():
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')

    if not from_date or not to_date:
        return jsonify({"error": "from_date и to_date параметры обязательны"}), 400

    statistics = calculate_food_order_statistics(from_date, to_date)
    return jsonify(statistics), 200

@app.route('/clear_order_history', methods=['DELETE'])
def clear_order_history():
    try:
        num_deleted_order_items = OrderItem.query.delete()
        num_deleted_orders = Order.query.delete()
        db.session.commit()
        return jsonify({
            "message": "История заказов успешно очищена",
            "deleted_orders": num_deleted_orders,
            "deleted_order_items": num_deleted_order_items
        }), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error occurred while clearing order history: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/clear_reservation_history', methods=['DELETE'])
def clear_reservation_history():
    try:
        num_deleted_reservations = Reservation.query.delete()
        db.session.commit()
        return jsonify({
            "message": "История бронирований успешно очищена",
            "deleted_reservations": num_deleted_reservations
        }), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error occurred while clearing reservation history: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/clear_support_requests', methods=['DELETE'])
def clear_support_requests_endpoint():
    return clear_support_requests()

@app.route('/clear_support_phones', methods=['DELETE'])
def clear_support_phones():
    return clear_phone_numbers()

@app.route('/cancel_order', methods=['DELETE'])
def cancel_order():
    user_email = request.args.get('user_email')
    table_number = request.args.get('table_number')

    if not user_email or not table_number:
        app.logger.error("Missing required parameters: user_email or table_number")
        return jsonify({"error": "user_email и table_number параметры обязательны"}), 400

    app.logger.info(f"Attempting to delete order for user_email: {user_email}, table_number: {table_number}")

    order = Order.query.filter_by(user_email=user_email, table_number=table_number).first()
    if order:
        for item in order.items:
            db.session.delete(item)
        db.session.delete(order)
        db.session.commit()
        app.logger.info(f"Order deleted successfully for user_email: {user_email}, table_number: {table_number}")
        return jsonify(message="Заказ успешно удалён")
    else:
        app.logger.error(f"Order not found for user_email: {user_email}, table_number: {table_number}")
        return jsonify(message="Заказ не найден"), 404



if __name__ == '__main__':
    port = int(os.getenv('PORT', '5000'))
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True, port=port)
