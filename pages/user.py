import streamlit as st

from database import users_collection, menu_collection


st.set_page_config(
    page_title="User - Smart Canteen",
    page_icon="👤",
    layout="centered"
)

st.title("👤 Smart Canteen")
st.subheader("Student Portal")


# -------------------------
# USER DASHBOARD
# -------------------------

if st.session_state.get("logged_in", False):

    user = st.session_state["user"]

    st.success(f"Welcome, {user['name']}!")

    st.write("### What would you like to do?")

    if st.session_state.get("show_menu", False):
        st.write("### 🍔 Canteen Menu")

    menu_items = list(
        menu_collection.find(
            {"available": True},
            {"_id": 0}
        )
    )

    for item in menu_items:
        st.write(
            f"**{item['item']}** — ₹{item['price']}"
        )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🍔 View Menu", use_container_width=True):
            st.session_state["show_menu"] = True
            st.rerun()

    with col2:
        st.button("🛒 My Cart", use_container_width=True)

    with col3:
        st.button("📦 My Orders", use_container_width=True)

    st.divider()

    st.write("### 👤 Account")
    st.write(f"**Name:** {user['name']}")
    st.write(f"**Email:** {user['email']}")

    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state.pop("user", None)
        st.rerun()

    st.stop()


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
            st.error("Please enter both email and password.")

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
                st.error("Invalid email or password.")


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
            st.error("Please fill in all fields.")

        elif password != confirm_password:
            st.error("Passwords do not match.")

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