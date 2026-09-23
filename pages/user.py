import streamlit as st

from database import users_collection, menu_collection


st.set_page_config(
    page_title="Smart Canteen",
    page_icon="🍽️",
    layout="wide"
)

st.markdown(
    """
    <style>

    /* Category navigation */
    [data-baseweb="tab"] {
        font-size: 1.15rem !important;
        font-weight: 600 !important;
        padding: 0.8rem 1.2rem !important;
    }

    [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------
# LOGIN / REGISTER
# -------------------------

if not st.session_state.get("logged_in", False):

    st.title("🍽️ Smart Canteen")
    st.subheader("Student Portal")

    tab1, tab2 = st.tabs(["Login", "Register"])


    # -------------------------
    # LOGIN
    # -------------------------

    with tab1:

        st.write("Login to your account")

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button("Login", use_container_width=True):

            if not email or not password:

                st.error(
                    "Please enter both email and password."
                )

            else:

                user = users_collection.find_one(
                    {
                        "email": email.lower().strip(),
                        "password": password
                    }
                )

                if user:

                    st.session_state["logged_in"] = True
                    st.session_state["user"] = user

                    st.rerun()

                else:

                    st.error(
                        "Invalid email or password."
                    )


    # -------------------------
    # REGISTER
    # -------------------------

    with tab2:

        st.write("Create a new account")

        name = st.text_input(
            "Full Name",
            key="register_name"
        )

        email = st.text_input(
            "Email",
            key="register_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="register_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="confirm_password"
        )

        if st.button(
            "Create Account",
            use_container_width=True
        ):

            if not name or not email or not password or not confirm_password:

                st.error(
                    "Please fill in all fields."
                )

            elif password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            else:

                email = email.lower().strip()

                existing_user = users_collection.find_one(
                    {"email": email}
                )

                if existing_user:

                    st.error(
                        "An account with this email already exists."
                    )

                else:

                    user = {
                        "name": name.strip(),
                        "email": email,
                        "password": password,
                        "role": "user"
                    }

                    users_collection.insert_one(user)

                    st.success(
                        "Account created successfully! "
                        "You can now login."
                    )

    st.stop()


# -------------------------
# CURRENT USER
# -------------------------

user = st.session_state["user"]


# -------------------------
# CART
# -------------------------

if "cart" not in st.session_state:
    st.session_state["cart"] = {}


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
# HEADER
# -------------------------

header_col1, header_col2 = st.columns([8, 1])

with header_col1:

    st.title("🍽️ Smart Canteen")
    st.caption("Student Portal")

with header_col2:

    with st.popover("👤", use_container_width=True):

        st.write(f"### {user['name']}")
        st.write(user["email"])

        st.divider()

        if st.button(
            "📦 My Orders",
            use_container_width=True
        ):
            st.switch_page("pages/orders.py")

        if st.button(
            "👤 Account Details",
            use_container_width=True
        ):
            pass

        st.divider()

        if st.button("🚪 Logout", use_container_width=True):

            st.session_state["logged_in"] = False
            st.session_state.pop("user", None)

            st.rerun()


st.divider()


# -------------------------
# WELCOME
# -------------------------

st.subheader(f"Good to see you, {user['name']}! 👋")
st.write("Choose a category and start ordering.")


# -------------------------
# CATEGORIES
# -------------------------

categories = sorted(
    list(
        set(
            item["category"]
            for item in menu_items
            if item.get("category")
        )
    )
)


if not categories:

    st.info("No menu categories available.")

else:

    category_tabs = st.tabs(categories)

    for tab, category in zip(category_tabs, categories):

        with tab:

            category_items = [
                item
                for item in menu_items
                if item.get("category") == category
            ]

            st.write(f"#### {category}")

            # Display items in rows of 4
            for i in range(0, len(category_items), 4):

                row_items = category_items[i:i + 4]

                columns = st.columns(4, gap="small")

                for col, item in zip(columns, row_items):

                    with col:

                        with st.container(border=True):

                            st.markdown(
                                f"**{item['item']}**"
                            )

                            st.write(
                                f"₹{item['price']}"
                            )

                            # -------------------------
                            # ITEM QUANTITY
                            # -------------------------

                            item_id = item["item_id"]
                            quantity = st.session_state["cart"].get(item_id, 0)


                            if quantity == 0:

                                if st.button(
                                    "🛒 Add",
                                    use_container_width=True,
                                    key=f"add_{item_id}"
                                ):

                                    st.session_state["cart"][item_id] = 1
                                    st.rerun()


                            else:

                                col_minus, col_qty, col_plus = st.columns(
                                    [1, 1, 1],
                                    gap="small"
                                )

                                with col_minus:

                                    if st.button(
                                        "−",
                                        use_container_width=True,
                                        key=f"minus_{item_id}"
                                    ):

                                        if quantity == 1:

                                            # Remove item completely
                                            del st.session_state["cart"][item_id]

                                        else:

                                            st.session_state["cart"][item_id] = quantity - 1

                                        st.rerun()


                                with col_qty:

                                    st.markdown(
                                        f"""
                                        <div style="
                                            text-align: center;
                                            padding-top: 7px;
                                            font-weight: 600;
                                            font-size: 1.05rem;
                                        ">
                                            {quantity}
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )


                                with col_plus:

                                    if st.button(
                                        "+",
                                        use_container_width=True,
                                        key=f"plus_{item_id}"
                                    ):

                                        st.session_state["cart"][item_id] = quantity + 1
                                        st.rerun()


# -------------------------
# CART
# -------------------------

st.divider()

st.subheader("🛒 Your Cart")


cart = st.session_state["cart"]


if not cart:

    st.info("Your cart is empty. Add some delicious food! 🍽️")


else:

    total_items = 0
    grand_total = 0


    # -------------------------
    # CART ITEMS
    # -------------------------

    for item in menu_items:

        item_id = item["item_id"]

        quantity = cart.get(item_id, 0)

        if quantity > 0:

            price = float(item["price"])

            subtotal = price * quantity

            total_items += quantity

            grand_total += subtotal


            col1, col2, col3, col4 = st.columns(
                [3, 1, 1, 1]
            )


            with col1:

                st.write(
                    f"**{item['item']}**"
                )


            with col2:

                st.write(
                    f"₹{price:.0f}"
                )


            with col3:

                st.write(
                    f"× {quantity}"
                )


            with col4:

                st.write(
                    f"**₹{subtotal:.0f}**"
                )


    st.divider()


    # -------------------------
    # CART TOTAL
    # -------------------------

    col1, col2 = st.columns([3, 1])


    with col1:

        st.write(
            f"**{total_items} item(s)**"
        )


    with col2:

        st.write(
            f"### ₹{grand_total:.0f}"
        )


    st.divider()


    # -------------------------
    # CHECKOUT BUTTON
    # -------------------------

    if st.button(
        f"💳 Proceed to Pay ₹{grand_total:.0f}",
        use_container_width=True
    ):

        # Remove any previous order from this session
        st.session_state.pop("current_order", None)

        st.session_state["checkout"] = True

        st.switch_page("pages/checkout.py")