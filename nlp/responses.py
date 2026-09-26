import random


def generate_response(
    intent,
    item=None,
    price=None
):

    if intent == "greeting":

        responses = [
            "Hello! 👋 How can I help you?",
            "Hi! What would you like to know?",
            "Hey! How can I help with your canteen order?"
        ]

        return random.choice(responses)


    if intent == "menu":

        responses = [
            "We have a variety of snacks, meals and beverages available.",
            "You can check our available snacks, meals and beverages from the menu.",
            "We have several food and beverage options available."
        ]

        return random.choice(responses)


    if intent == "price":

        if item and price is not None:

            responses = [
                f"The {item} costs ₹{price}.",
                f"{item} is priced at ₹{price}.",
                f"You can get a {item} for ₹{price}."
            ]

            return random.choice(responses)

        return "Sure! Tell me which food item you want the price of."


    if intent == "timings":

        responses = [
            "The canteen is open during college hours.",
            "The canteen operates during regular college hours.",
            "You can visit the canteen during college working hours."
        ]

        return random.choice(responses)


    if intent == "how_to_order":

        return (
            "To place an order, open the User Portal, "
            "choose your food items, add them to the cart, "
            "and proceed to checkout."
        )


    if intent == "order_status":

        return (
            "You can check your order status from the "
            "My Orders section using your order token."
        )


    if intent == "payment":

        return (
            "You can proceed to checkout after adding "
            "your food items to the cart."
        )


    if intent == "popular_items":

        return (
            "Some popular choices include Vada Pav, "
            "Masala Dosa, Veg Sandwich and Tea."
        )


    if intent == "canteen_info":

        return (
            "Smart Canteen allows students to order food "
            "online and collect it using their token number."
        )


    if intent == "thanks":

        responses = [
            "You're welcome! 😊",
            "Happy to help! 😊",
            "Anytime!"
        ]

        return random.choice(responses)


    return (
        "Sorry, I didn't understand that. "
        "Please ask something related to the canteen."
    )