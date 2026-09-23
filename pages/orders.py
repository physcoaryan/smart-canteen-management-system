import streamlit as st

from database import orders_collection


st.set_page_config(
    page_title="My Orders - Smart Canteen",
    page_icon="📦",
    layout="centered"
)


# -------------------------
# LOGIN CHECK
# -------------------------

if not st.session_state.get("logged_in", False):

    st.warning("Please login to view your orders.")
    st.stop()


# -------------------------
# USER
# -------------------------

user = st.session_state["user"]


# -------------------------
# HEADER
# -------------------------

st.title("📦 My Orders")

st.write(
    f"Orders placed by **{user['name']}**"
)

st.divider()


# -------------------------
# FETCH USER ORDERS
# -------------------------

orders = list(
    orders_collection.find(
        {
            "user_email": user["email"]
        },
        {
            "_id": 0
        }
    ).sort(
        "created_at",
        -1
    )
)


# -------------------------
# NO ORDERS
# -------------------------

if not orders:

    st.info(
        "You haven't placed any orders yet."
    )

    st.stop()


# -------------------------
# DISPLAY ORDERS
# -------------------------

for order in orders:

    with st.container(border=True):

        st.subheader(
            f"🎟️ Token: {order['token_number']}"
        )

        st.write(
            f"📅 {order['created_at'][:10]}"
            f"   🕐 {order['created_at'][11:]}"
        )

        st.write(
            f"📦 Status: **{order['order_status']}**"
        )

        st.write(
            f"💳 Payment: **{order['payment_status']}**"
        )

        st.divider()

        for item in order["items"]:

            st.write(
                f"**{item['item']}** "
                f"× {item['quantity']} "
                f"— ₹{item['subtotal']:.0f}"
            )

        st.divider()

        st.write(
            f"### Total: ₹{order['total_amount']:.0f}"
        )