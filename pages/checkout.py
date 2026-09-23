from datetime import datetime
from zoneinfo import ZoneInfo
import uuid

import streamlit as st

from database import (
    menu_collection,
    orders_collection,
    get_next_token
)

st.set_page_config(
    page_title="Order Confirmation - Smart Canteen",
    page_icon="🎟️",
    layout="centered"
)


# -------------------------
# CHECKOUT CHECK
# -------------------------

if not st.session_state.get("checkout", False):

    st.warning("No active order.")
    st.stop()


# -------------------------
# USER
# -------------------------

user = st.session_state["user"]

cart = st.session_state.get("cart", {})


# -------------------------
# LOAD MENU
# -------------------------

menu_items = list(
    menu_collection.find(
        {"available": True},
        {"_id": 0}
    )
)


# -------------------------
# CREATE ORDER ONCE
# -------------------------

if "current_order" not in st.session_state:

    order_items = []
    total_amount = 0
    total_items = 0

    for item in menu_items:

        item_id = item["item_id"]

        quantity = cart.get(item_id, 0)

        if quantity > 0:

            price = float(item["price"])

            subtotal = price * quantity

            order_items.append({
                "item_id": item_id,
                "item": item["item"],
                "price": price,
                "quantity": quantity,
                "subtotal": subtotal
            })

            total_amount += subtotal
            total_items += quantity


    # Current Indian date and time
    order_time = datetime.now(
        ZoneInfo("Asia/Kolkata")
    )


    # Generate token
    token_number = get_next_token()


    # Create order
    order = {
        "order_id": str(uuid.uuid4()),
        "token_number": token_number,

        "user_name": user["name"],
        "user_email": user["email"],

        "items": order_items,

        "total_items": total_items,
        "total_amount": total_amount,

        "payment_status": "Successful",
        "order_status": "Placed",

        "created_at": order_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }


    # Save order to MongoDB
    orders_collection.insert_one(order)


    # Keep order available for this session
    st.session_state["current_order"] = order


    # Clear cart
    st.session_state["cart"] = {}


# -------------------------
# CURRENT ORDER
# -------------------------

order = st.session_state["current_order"]


# -------------------------
# ORDER CONFIRMATION
# -------------------------

st.title("🎉 Order Confirmed!")

st.success(
    "Payment Successful"
)


st.subheader("🎟️ Your Token")

st.info(
    f"🎟️ **Token Number: {order['token_number']}**"
)


# -------------------------
# ORDER DETAILS
# -------------------------

st.subheader("🧾 Order Summary")


for item in order["items"]:

    col1, col2, col3, col4 = st.columns(
        [4, 1, 1, 1]
    )

    with col1:
        st.write(
            f"**{item['item']}**"
        )

    with col2:
        st.write(
            f"₹{item['price']:.0f}"
        )

    with col3:
        st.write(
            f"× {item['quantity']}"
        )

    with col4:
        st.write(
            f"**₹{item['subtotal']:.0f}**"
        )


st.divider()


# -------------------------
# TOTAL
# -------------------------

st.write(
    f"### Total: ₹{order['total_amount']:.0f}"
)


# -------------------------
# DATE & TIME
# -------------------------

st.write(
    f"📅 **Date:** {order['created_at'][:10]}"
)

st.write(
    f"🕐 **Time:** {order['created_at'][11:]}"
)


st.write(
    f"📦 **Status:** {order['order_status']}"
)