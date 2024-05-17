from flask import Flask, request, jsonify
from models import db, Reservation
from datetime import datetime, timedelta

app = Flask(__name__)


def reserve_seat():
    data = request.json
    if not data:
        app.logger.error("No data provided")
        return jsonify({"error": "No data provided"}), 400

    required_fields = ['userEmail', 'placeNumber', 'date', 'time', 'duration', 'userName']
    if not all(key in data for key in required_fields):
        return jsonify({"error": "Необходимые данные отсутствуют"}), 400

    try:
        datetime_string = f"{data['date']} {data['time']}"
        combined_datetime = datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S')
    except ValueError as e:
        return jsonify({"error": "Некорректный формат даты или времени: " + str(e)}), 400

    new_reservation = Reservation(
        user_email=data['userEmail'],
        user_name=data['userName'],
        seat_number=data['placeNumber'],
        date=combined_datetime.date(),
        time=combined_datetime,
        duration=data['duration']
    )
    app.logger.debug("Attempting to create reservation with data: %s", data)
    db.session.add(new_reservation)
    db.session.commit()
    app.logger.debug("Reservation created with ID: %s", new_reservation.id)
    return jsonify(message="Место успешно забронировано", reservation_id=new_reservation.id)


# В функции get_reservations измените возвращаемое значение:
def get_reservations():
    reservations = Reservation.query.all()
    reservations_list = [
        {
            'reservation_id': reservation.id,
            'user_name': reservation.user_name,
            'user_email': reservation.user_email,
            'seat_number': reservation.seat_number,
            'duration': reservation.duration,
            'time': reservation.time.strftime('%Y-%m-%d %H:%M:%S'),
        } for reservation in reservations
    ]
    return jsonify(reservations_list)  # Изменено для возврата массива напрямую


def get_user_reservations():
    user_email = request.args.get('email')
    if not user_email:
        return jsonify({"error": "Email is required"}), 400
    reservations = Reservation.query.filter_by(user_email=user_email).all()
    return jsonify([{
        'id': r.id,
        'date': r.date.strftime('%Y-%m-%d'),
        'time': r.time.strftime('%H:%M:%S'),
        'duration': r.duration,
        'seat_number': r.seat_number
    } for r in reservations]), 200



def check_availability():
    data = request.json
    if not data or not all(key in data for key in ['placeNumber', 'date', 'time', 'duration']):
        return jsonify({"error": "Missing required data"}), 400

    seat_number = data['placeNumber']
    start_time = datetime.strptime(f"{data['date']} {data['time']}", '%Y-%m-%d %H:%M:%S')
    duration_hours = int(data['duration'])  # Продолжительность в часах
    end_time = start_time + timedelta(hours=duration_hours)  # Переводим часы в timedelta

    reservations = Reservation.query.filter(
        Reservation.seat_number == seat_number,
        Reservation.date == start_time.date()
    ).all()

    for reservation in reservations:
        reservation_end_time = reservation.time + timedelta(hours=reservation.duration)
        if start_time < reservation_end_time and end_time > reservation.time:
            return jsonify(available=False, message="This slot overlaps with an existing reservation"), 409

    return jsonify(available=True)


def cancel_reservation(reservation_id):
    reservation = Reservation.query.get(reservation_id)
    if reservation:
        db.session.delete(reservation)
        db.session.commit()
        return jsonify(message="Бронь успешно отменена")
    return jsonify(message="Бронь не найдена"), 404