import streamlit as st
import html

from nlp.chatbot import process_message


# -------------------------
# PAGE CONFIG
# -------------------------

st.set_page_config(
    page_title="Smart Canteen Chatbot",
    page_icon="🤖",
    layout="wide"
)


# -------------------------
# CUSTOM CSS
# -------------------------

st.markdown(
    """
    <style>

    /* =====================================================
       MAIN PAGE
       ===================================================== */

    .block-container {
        padding-top: 2rem;
        padding-right: 350px;
        padding-bottom: 6rem;
    }


    /* =====================================================
       RIGHT FIXED CHATBOT PANEL
       ===================================================== */

    .st-key-right_panel {

        position: fixed;

        top: 0;
        right: 0;

        width: 320px;
        height: 100vh;

        background: #17191f;

        border-left: 1px solid #30333b;

        padding: 35px 25px;

        z-index: 999999;

        overflow-y: auto;

        box-sizing: border-box;
    }


    /* =====================================================
       RIGHT PANEL CONTENT
       ===================================================== */

    .side-title {

        font-size: 25px;
        font-weight: 700;

        color: white;

        margin-bottom: 8px;
    }


    .side-caption {

        font-size: 14px;

        color: #aab0bd;

        margin-bottom: 30px;
    }


    .side-section {

        font-size: 14px;

        font-weight: 600;

        color: #aab0bd;

        margin-top: 25px;

        margin-bottom: 10px;
    }


    /* =====================================================
       CHAT MESSAGES
       ===================================================== */

    .chat-row {

        display: flex;

        width: 100%;

        margin-bottom: 18px;
    }


    .assistant-row {

        justify-content: flex-start;
    }


    .user-row {

        justify-content: flex-end;
    }


    .chat-bubble {

        max-width: 70%;

        padding: 13px 17px;

        border-radius: 15px;

        font-size: 16px;

        line-height: 1.5;

        color: white;
    }


    .assistant-bubble {

        background: #1b1e26;

        border-top-left-radius: 4px;
    }


    .user-bubble {

        background: #26384d;

        border-top-right-radius: 4px;
    }


    .chat-icon {

        margin-right: 8px;

        font-size: 17px;
    }


    /* =====================================================
       CHAT INPUT - DESKTOP
       ===================================================== */

    div[data-testid="stChatInput"] {

        position: fixed !important;

        /*
        Streamlit sidebar ≈ 18%
        Right chatbot panel = 320px
        */

        left: 18% !important;

        right: 320px !important;

        bottom: 20px !important;

        width: auto !important;

        max-width: none !important;

        /*
        Remove Streamlit's default centering
        */

        transform: none !important;

        margin: 0 !important;

        z-index: 999998 !important;

        box-sizing: border-box !important;
    }


    /* =====================================================
       CHAT INPUT INNER ELEMENT
       ===================================================== */

    div[data-testid="stChatInput"] > div {

        width: 100% !important;

        box-sizing: border-box !important;
    }


    /* =====================================================
       MOBILE
       ===================================================== */

    @media (max-width: 800px) {

        /*
        Hide right panel on small screens.
        This gives the chatbot the complete screen.
        */

        .st-key-right_panel {

            display: none;
        }


        /*
        Remove the desktop right padding.
        */

        .block-container {

            padding-right: 1rem;

            padding-left: 1rem;

            padding-bottom: 110px;
        }


        /*
        Chat bubbles can use more width.
        */

        .chat-bubble {

            max-width: 85%;
        }


        /*
        Chat input uses the entire mobile width.
        */

        div[data-testid="stChatInput"] {

            left: 10px !important;

            right: 10px !important;

            bottom: 10px !important;

            width: auto !important;

            max-width: none !important;

            transform: none !important;

            margin: 0 !important;
        }

    }


    /* =====================================================
       VERY SMALL PHONES
       ===================================================== */

    @media (max-width: 480px) {

        .chat-bubble {

            max-width: 90%;

            font-size: 15px;
        }


        div[data-testid="stChatInput"] {

            left: 5px !important;

            right: 5px !important;

            bottom: 5px !important;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# -------------------------
# RIGHT FIXED PANEL
# -------------------------

with st.container(key="right_panel"):

    st.markdown(
        """
        <div class="side-title">
            🤖 Smart Canteen Assistant
        </div>

        <div class="side-caption">
            Ask me about the menu, prices, orders and canteen.
        </div>
        """,
        unsafe_allow_html=True
    )


    # -------------------------
    # HOME BUTTON
    # -------------------------

    if st.button(
        "🏠  Home",
        use_container_width=True
    ):

        st.switch_page("app.py")


    # -------------------------
    # SAMPLE QUESTIONS
    # -------------------------

    st.markdown(
        '<div class="side-section">💡 Try asking</div>',
        unsafe_allow_html=True
    )


    if st.button(
        "💰 What is the price of tea?",
        use_container_width=True
    ):

        st.session_state.sample_question = (
            "What is the price of tea?"
        )


    if st.button(
        "📋 What food do you have?",
        use_container_width=True
    ):

        st.session_state.sample_question = (
            "What food do you have?"
        )


    if st.button(
        "🛒 How do I place an order?",
        use_container_width=True
    ):

        st.session_state.sample_question = (
            "How do I place an order?"
        )


    if st.button(
        "📦 Where is my order?",
        use_container_width=True
    ):

        st.session_state.sample_question = (
            "Where is my order?"
        )


    if st.button(
        "⭐ What should I try?",
        use_container_width=True
    ):

        st.session_state.sample_question = (
            "What should I try?"
        )


# -------------------------
# CHAT HISTORY
# -------------------------

if "chat_messages" not in st.session_state:

    st.session_state.chat_messages = [

        {
            "role": "assistant",

            "content": (
                "Hello! 👋 I'm your Smart Canteen Assistant. "
                "How can I help you?"
            )
        }

    ]


# -------------------------
# DISPLAY CHAT
# -------------------------

for message in st.session_state.chat_messages:

    message_text = html.escape(
        message["content"],
        quote=False
    )


    # -------------------------
    # ASSISTANT MESSAGE
    # -------------------------

    if message["role"] == "assistant":

        assistant_html = f"""
<div class="chat-row assistant-row">

    <div class="chat-bubble assistant-bubble">

        <span class="chat-icon">🤖</span>

        {message_text}

    </div>

</div>
"""

        st.html(assistant_html)


    # -------------------------
    # USER MESSAGE
    # -------------------------

    else:

        user_html = f"""
<div class="chat-row user-row">

    <div class="chat-bubble user-bubble">

        {message_text}

        <span class="chat-icon">👤</span>

    </div>

</div>
"""

        st.html(user_html)


# -------------------------
# SAMPLE QUESTION HANDLING
# -------------------------

sample_question = st.session_state.pop(
    "sample_question",
    None
)


# -------------------------
# CHAT INPUT
# -------------------------

user_input = st.chat_input(
    "Ask something about the canteen..."
)


# -------------------------
# SELECT INPUT
# -------------------------

if sample_question:

    user_input = sample_question


# -------------------------
# PROCESS MESSAGE
# -------------------------

if user_input:

    # -------------------------
    # STORE USER MESSAGE
    # -------------------------

    st.session_state.chat_messages.append(
        {
            "role": "user",

            "content": user_input
        }
    )


    # -------------------------
    # NLP PIPELINE
    # -------------------------

    result = process_message(
        user_input
    )


    response = result["response"]


    # -------------------------
    # STORE ASSISTANT RESPONSE
    # -------------------------

    st.session_state.chat_messages.append(
        {
            "role": "assistant",

            "content": response
        }
    )


    # -------------------------
    # REFRESH
    # -------------------------

    st.rerun()