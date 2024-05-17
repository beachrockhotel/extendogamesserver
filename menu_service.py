import logging
from flask import Flask, request, jsonify
from models import db, MenuItem, Order, OrderItem

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_menu_item():
    data = request.json
    name = data.get('name')
    price = data.get('price')
    image_url = data.get('image_url')

    if not name or price is None:
        return jsonify({"error": "Имя или цена пропущены"}), 400

    new_item = MenuItem(name=name, price=price, image_url=image_url)
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"message": "Позиция была создана", "id": new_item.id, "image_url": image_url}), 201


def get_menu():
    menu_items = MenuItem.query.all()
    return jsonify(menu=[{'id': item.id, 'name': item.name, 'price': item.price, 'image_url': item.image_url} for item in menu_items])


def make_order():
    data = request.json
    user_name = data.get('user_name')
    user_email = data.get('user_email')
    table_number = data.get('table_number', 'Самовывоз')
    items_data = data.get('items')

    if not all([user_name, user_email, items_data]):
        logger.error("Missing required user information or item list")
        return jsonify({"error": "Missing required user information or item list"}), 400

    new_order = Order(user_name=user_name, user_email=user_email, table_number=table_number, total_price=0)
    db.session.add(new_order)

    total_price = 0
    try:
        for item_data in items_data:
            item_name = item_data.get('name')
            quantity = item_data.get('quantity', 1)
            if quantity < 1:
                logger.warning(f"Invalid quantity for item: {item_name}")
                continue

            menu_item = MenuItem.query.filter_by(name=item_name).first()
            if not menu_item:
                logger.warning(f"Item not found: {item_name}")
                continue

            item_total = menu_item.price * quantity
            total_price += item_total
            order_item = OrderItem(order=new_order, menu_item=menu_item, quantity=quantity, price_at_time_of_order=menu_item.price)
            db.session.add(order_item)

        new_order.total_price = total_price
        db.session.commit()
        logger.info(f"Order created successfully: {new_order.id}")
        return jsonify({"success": True, "order_id": new_order.id, "total_price": total_price, "table_number": table_number}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error while creating order: {e}")
        return jsonify({"error": str(e)}), 400



def get_orders():
    orders = Order.query.all()
    return jsonify(orders=[
        {
            'id': order.id,
            'user_name': order.user_name,
            'user_email': order.user_email,
            'table_number': order.table_number,
            'items': aggregate_items(order.items),
            'total_price': order.total_price,
            'order_time': order.order_time.strftime("%Y-%m-%d %H:%M:%S")
        } for order in orders
    ])

def aggregate_items(items):
    aggregated = {}
    for item in items:
        if item.menu_item.name not in aggregated:
            aggregated[item.menu_item.name] = {
                'name': item.menu_item.name,
                'quantity': item.quantity,
                'price': item.price_at_time_of_order
            }
        else:
            aggregated[item.menu_item.name]['quantity'] += item.quantity
    return list(aggregated.values())



def get_user_orders(user_email):
    orders = Order.query.filter(Order.user_email == user_email).all()
    if not orders:
        return jsonify({"message": "No orders found for this user"}), 404
    return jsonify([{
        'id': order.id,
        'user_name': order.user_name,
        'user_email': order.user_email,
        'table_number': order.table_number,
        'total_price': order.total_price,
        'order_date': order.order_time.strftime('%Y-%m-%d %H:%M:%S'),
        'items': [{
            'name': item.menu_item.name,
            'quantity': item.quantity,
            'price': item.price_at_time_of_order
        } for item in order.items]
    } for order in orders])