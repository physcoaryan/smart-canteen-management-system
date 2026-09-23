import streamlit as st

from database import users_collection, orders_collection
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
from zoneinfo import ZoneInfo


st.set_page_config(
    page_title="Worker Portal - Smart Canteen",
    page_icon="👨‍🍳",
    layout="wide"
)

st_autorefresh(
    interval=2000,
    key="worker_dashboard_refresh"
)


# -------------------------
# WORKER LOGIN
# -------------------------

if not st.session_state.get("worker_logged_in", False):

    st.write("Login to manage canteen orders.")

    email = st.text_input(
        "Email",
        key="worker_login_email"
    )

    password = st.text_input(
        "Password",
        type="password",
        key="worker_login_password"
    )

    if st.button(
        "Login",
        use_container_width=True
    ):

        if not email or not password:

            st.error(
                "Please enter both email and password."
            )

        else:

            worker = users_collection.find_one(
                {
                    "email": email.lower().strip(),
                    "password": password,
                    "role": "worker"
                }
            )

            if worker:

                st.session_state["worker_logged_in"] = True
                st.session_state["worker"] = worker

                st.rerun()

            else:

                st.error(
                    "Invalid worker email or password."
                )

    st.stop()


# -------------------------
# WORKER
# -------------------------

worker = st.session_state["worker"]


# -------------------------
# HEADER
# -------------------------

header_col1, header_col2 = st.columns([6, 1])

with header_col1:

    st.title("👨‍🍳 Production Dashboard")

    st.caption(
        f"Welcome, {worker['name']}"
    )

with header_col2:

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state["worker_logged_in"] = False
        st.session_state.pop("worker", None)

        st.rerun()


# -------------------------
# FETCH ACTIVE ORDERS
# -------------------------

today = datetime.now(
    ZoneInfo("Asia/Kolkata")
).strftime("%Y-%m-%d")


orders = list(
    orders_collection.find(
        {
            "order_status": "Placed",
            "created_at": {
                "$regex": f"^{today}"
            }
        },
        {
            "_id": 0
        }
    ).sort(
        "created_at",
        1
    )
)


# -------------------------
# CALCULATE ACTIVE ITEMS
# -------------------------

active_items = {}

total_active_items = 0

for order in orders:

    for item in order["items"]:

        item_name = item["item"]
        quantity = item["quantity"]

        active_items[item_name] = (
            active_items.get(item_name, 0) + quantity
        )

        total_active_items += quantity


# -------------------------
# HEADER STATS
# -------------------------

st.write(
    f"**{len(orders)} Active Orders** "
    f"| **{total_active_items} Items**"
)

st.divider()


# -------------------------
# TWO COLUMN DASHBOARD
# -------------------------

left_col, right_col = st.columns(
    [1, 1],
    gap="large"
)


# =========================================================
# LEFT — ORDERS
# =========================================================

with left_col:

    st.subheader("📋 Orders")

    if not orders:

        st.info(
            "No active orders right now."
        )

    else:

        for order in orders:

            with st.container(border=True):

                st.markdown(
                    f"### 🎟️ {order['token_number']}"
                )

                for item in order["items"]:

                    st.write(
                        f"**{item['item']}** "
                        f"× {item['quantity']}"
                    )

                st.caption(
                    f"Order placed at "
                    f"{order['created_at'][11:]}"
                )


                if st.button(
                    "✅ Order Given",
                    use_container_width=True,
                    key=f"complete_{order['order_id']}"
                ):

                    orders_collection.update_one(
                        {
                            "order_id": order["order_id"]
                        },
                        {
                            "$set": {
                                "order_status": "Completed"
                            }
                        }
                    )

                    st.rerun()


# =========================================================
# RIGHT — TO MAKE
# =========================================================

with right_col:

    st.subheader("🔥 To Make")

    if not active_items:

        st.info(
            "Nothing to prepare."
        )

    else:

        for item_name, quantity in active_items.items():

            with st.container(border=True):

                st.markdown(
                    f"**{item_name}**"
                )

                st.write(
                    f"× {quantity}"
                )

