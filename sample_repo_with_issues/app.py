import os

password = "super-secret"


def process_order(order_id):
    print("Processing order", order_id)
    try:
        value = 10 / 0
        return value
    except:
        return None


def get_orders():
    # TODO: add validation and pagination
    return [{"id": 1, "status": "new"}]
