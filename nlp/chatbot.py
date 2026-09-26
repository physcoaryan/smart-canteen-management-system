from nlp.engine import predict_intent
from nlp.entities import find_item
from nlp.responses import generate_response

from database import menu_collection


def get_item_price(item_name):

    if not item_name:
        return None

    item = menu_collection.find_one(
        {
            "item": item_name
        }
    )

    if item:
        return item.get("price")

    return None


def process_message(user_text):

    # -------------------------
    # INTENT DETECTION
    # -------------------------

    intent, score = predict_intent(
        user_text
    )

    # -------------------------
    # ENTITY DETECTION
    # -------------------------

    item = find_item(
        user_text
    )

    # -------------------------
    # PRICE LOOKUP
    # -------------------------

    price = None

    if intent == "price" and item:

        price = get_item_price(
            item
        )

    # -------------------------
    # GENERATE RESPONSE
    # -------------------------

    response = generate_response(
        intent=intent,
        item=item,
        price=price
    )

    return {
        "intent": intent,
        "score": score,
        "item": item,
        "response": response
    }