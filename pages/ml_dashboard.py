import streamlit as st
import pandas as pd
import joblib
from pathlib import Path


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Canteen ML Dashboard",
    page_icon="🧠",
    layout="wide"
)


# =====================================================
# PATHS
# =====================================================

BASE_DIR = Path(__file__).parent.parent

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "final_demand_model.pkl"
)

DATA_PATH = (
    BASE_DIR
    / "data"
    / "canteen_sales.csv"
)


# =====================================================
# LOAD MODEL
# =====================================================

@st.cache_resource
def load_model():

    return joblib.load(MODEL_PATH)


model = load_model()


# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data
def load_data():

    data = pd.read_csv(DATA_PATH)

    # Convert date
    data["date"] = pd.to_datetime(
        data["date"]
    )

    # Convert time
    data["time_slot"] = pd.to_datetime(
        data["time_slot"],
        format="%H:%M:%S"
    ).dt.time

    return data


df = load_data()


# =====================================================
# HEADER
# =====================================================

st.title(
    "🧠 Canteen Demand Intelligence"
)

st.write(
    "Explore how different conditions can affect "
    "food demand using the trained machine learning model."
)

st.divider()


# =====================================================
# WHAT-IF DEMAND SIMULATOR
# =====================================================

st.header(
    "🔬 What-If Demand Simulator"
)

st.write(
    "First select a food item and date to establish "
    "the normal demand. Then change conditions to "
    "simulate a different scenario."
)


# =====================================================
# NORMAL SCENARIO
# =====================================================

st.subheader(
    "📊 Normal Scenario"
)


# =====================================================
# ITEM SELECTION
# =====================================================

item = st.selectbox(
    "🍴 Select Food Item",
    sorted(
        df["item"].unique()
    )
)


# =====================================================
# DATE SELECTION
# =====================================================

selected_date = st.date_input(
    "📅 Select Date"
)

selected_date = pd.Timestamp(
    selected_date
)


# =====================================================
# FIND HISTORICAL DATA
# =====================================================

item_date_data = df[
    (df["item"] == item)
    &
    (df["date"] == selected_date)
]


# =====================================================
# NO DATA
# =====================================================

if item_date_data.empty:

    st.warning(
        "No historical data is available for "
        f"**{item}** on "
        f"**{selected_date.strftime('%d %B %Y')}**."
    )

    st.stop()


# =====================================================
# HISTORICAL DATA FOUND
# =====================================================

st.success(
    f"Historical data found for **{item}** on "
    f"**{selected_date.strftime('%d %B %Y')}**."
)


# =====================================================
# GET ITEM INFORMATION
# =====================================================

item_info = df[
    df["item"] == item
].iloc[0]

category = item_info["category"]
price = item_info["price"]


# =====================================================
# DETERMINE DATE CONDITIONS
# =====================================================

day_of_week = item_date_data[
    "day_of_week"
].iloc[0]

month = int(
    item_date_data["month"].iloc[0]
)

is_saturday = int(
    item_date_data["is_saturday"].iloc[0]
)

is_sunday = int(
    item_date_data["is_sunday"].iloc[0]
)

is_exam_period = int(
    item_date_data["is_exam_period"].iloc[0]
)

is_holiday = int(
    item_date_data["is_holiday"].iloc[0]
)

college_event = item_date_data[
    "college_event"
].iloc[0]


# =====================================================
# CONVERT COLLEGE EVENT TO YES / NO
# =====================================================

def event_to_label(value):

    if str(value).lower() in [
        "1",
        "yes",
        "true"
    ]:
        return "Yes"

    return "No"


normal_event_label = event_to_label(
    college_event
)


# =====================================================
# DETERMINE NORMAL WEATHER
# =====================================================

weather = (
    item_date_data["weather"]
    .mode()
    .iloc[0]
)


# =====================================================
# NORMAL SCENARIO TIME
# =====================================================

normal_time = (
    item_date_data["time_slot"]
    .value_counts()
    .idxmax()
)

normal_hour = normal_time.hour
normal_minute = normal_time.minute

normal_time_index = (
    normal_hour * 60
    + normal_minute
)


# =====================================================
# NORMAL SCENARIO INFORMATION
# =====================================================

st.markdown(
    "### 📌 Historical Conditions"
)

info_col1, info_col2, info_col3, info_col4 = st.columns(4)


with info_col1:

    st.metric(
        "Day",
        day_of_week
    )


with info_col2:

    st.metric(
        "Time",
        normal_time.strftime("%H:%M")
    )


with info_col3:

    st.metric(
        "Weather",
        weather
    )


with info_col4:

    st.metric(
        "Exam",
        "Yes" if is_exam_period == 1 else "No"
    )


condition_col1, condition_col2, condition_col3, condition_col4 = st.columns(4)


with condition_col1:

    st.metric(
        "Holiday",
        "Yes" if is_holiday == 1 else "No"
    )


with condition_col2:

    st.metric(
        "College Event",
        normal_event_label
    )


with condition_col3:

    st.metric(
        "Category",
        category
    )


with condition_col4:

    st.metric(
        "Price",
        f"₹{price}"
    )


# =====================================================
# PREDICTION FUNCTION
# =====================================================

def make_prediction(
    day_of_week,
    month,
    item,
    category,
    price,
    is_saturday,
    is_sunday,
    is_exam_period,
    is_holiday,
    weather,
    college_event,
    hour,
    minute
):

    time_index = (
        hour * 60
        + minute
    )

    input_data = pd.DataFrame([
        {
            "day_of_week": day_of_week,
            "month": month,
            "item": item,
            "category": category,
            "price": price,
            "is_saturday": is_saturday,
            "is_sunday": is_sunday,
            "is_exam_period": is_exam_period,
            "is_holiday": is_holiday,
            "weather": weather,
            "college_event": college_event,
            "hour": hour,
            "minute": minute,
            "time_index": time_index
        }
    ])

    prediction = model.predict(
        input_data
    )[0]

    return max(
        0,
        round(prediction)
    )


# =====================================================
# NORMAL SCENARIO PREDICTION
# =====================================================

normal_prediction = make_prediction(
    day_of_week=day_of_week,
    month=month,
    item=item,
    category=category,
    price=price,
    is_saturday=is_saturday,
    is_sunday=is_sunday,
    is_exam_period=is_exam_period,
    is_holiday=is_holiday,
    weather=weather,
    college_event=college_event,
    hour=normal_hour,
    minute=normal_minute
)


# =====================================================
# NORMAL DEMAND DISPLAY
# =====================================================

st.divider()

st.markdown(
    "### 📈 Normal Expected Demand"
)

normal_col1, normal_col2 = st.columns(2)


with normal_col1:

    st.metric(
        "Expected Demand",
        f"{normal_prediction} units"
    )


with normal_col2:

    st.info(
        f"Under the historical conditions for "
        f"**{item}** on "
        f"**{selected_date.strftime('%d %B %Y')}**, "
        f"the model predicts approximately "
        f"**{normal_prediction} units**."
    )


# =====================================================
# WHAT-IF SCENARIO
# =====================================================

st.divider()

st.subheader(
    "🔬 What-If Scenario"
)

st.write(
    "Keep the same food item and date, but change "
    "the conditions to see how demand could change."
)


# =====================================================
# WHAT-IF INPUTS — ROW BY ROW
# =====================================================


# -----------------------------------------------------
# QUESTION 1 — TIME
# -----------------------------------------------------

st.markdown(
    "**1️⃣ What time should we simulate?**"
)

whatif_hour = st.slider(
    "Hour",
    min_value=8,
    max_value=18,
    value=normal_hour,
    key="whatif_hour"
)

whatif_minute = st.slider(
    "Minute",
    min_value=0,
    max_value=45,
    value=normal_minute,
    step=15,
    key="whatif_minute"
)

st.caption(
    f"Selected time: **{whatif_hour:02d}:{whatif_minute:02d}**"
)


# -----------------------------------------------------
# QUESTION 2 — WEATHER
# -----------------------------------------------------

st.markdown(
    "**2️⃣ What weather should we simulate?**"
)

weather_options = sorted(
    df["weather"].unique()
)

whatif_weather = st.selectbox(
    "Weather",
    weather_options,
    index=weather_options.index(weather),
    key="whatif_weather"
)


# -----------------------------------------------------
# QUESTION 3 — EXAM
# -----------------------------------------------------

st.markdown(
    "**3️⃣ Is there an examination period?**"
)

whatif_exam = st.selectbox(
    "Exam Period",
    [0, 1],
    index=is_exam_period,
    format_func=lambda x:
        "Yes" if x == 1 else "No",
    key="whatif_exam"
)


# -----------------------------------------------------
# QUESTION 4 — HOLIDAY
# -----------------------------------------------------

st.markdown(
    "**4️⃣ Is it a holiday?**"
)

whatif_holiday = st.selectbox(
    "Holiday",
    [0, 1],
    index=is_holiday,
    format_func=lambda x:
        "Yes" if x == 1 else "No",
    key="whatif_holiday"
)


# -----------------------------------------------------
# QUESTION 5 — COLLEGE EVENT
# -----------------------------------------------------

st.markdown(
    "**5️⃣ Is there a college event?**"
)

whatif_event_label = st.selectbox(
    "College Event",
    ["No", "Yes"],
    index=(
        1
        if normal_event_label == "Yes"
        else 0
    ),
    key="whatif_event"
)


# =====================================================
# CONVERT EVENT YES / NO TO MODEL VALUE
# =====================================================

if whatif_event_label == "Yes":

    whatif_event = 1

else:

    whatif_event = 0


# =====================================================
# WHAT-IF PREDICTION
# =====================================================

whatif_prediction = make_prediction(
    day_of_week=day_of_week,
    month=month,
    item=item,
    category=category,
    price=price,
    is_saturday=is_saturday,
    is_sunday=is_sunday,
    is_exam_period=whatif_exam,
    is_holiday=whatif_holiday,
    weather=whatif_weather,
    college_event=whatif_event,
    hour=whatif_hour,
    minute=whatif_minute
)


# =====================================================
# COMPARE DEMAND
# =====================================================

demand_difference = (
    whatif_prediction
    - normal_prediction
)


if normal_prediction != 0:

    percentage_change = (
        demand_difference
        / normal_prediction
    ) * 100

else:

    percentage_change = 0


# =====================================================
# WHAT-IF RESULT
# =====================================================

st.divider()

st.markdown(
    "### 🔮 What-If Prediction"
)

result_col1, result_col2, result_col3 = st.columns(3)


with result_col1:

    st.metric(
        "Normal Demand",
        f"{normal_prediction} units"
    )


with result_col2:

    st.metric(
        "What-If Demand",
        f"{whatif_prediction} units"
    )


with result_col3:

    st.metric(
        "Change",
        f"{demand_difference:+d} units",
        delta=f"{percentage_change:+.1f}%"
    )


# =====================================================
# INTERPRETATION
# =====================================================

if demand_difference > 0:

    st.success(
        f"📈 Demand is expected to **increase** by "
        f"**{demand_difference} units "
        f"({percentage_change:+.1f}%)** "
        f"compared with the normal scenario."
    )

elif demand_difference < 0:

    st.warning(
        f"📉 Demand is expected to **decrease** by "
        f"**{abs(demand_difference)} units "
        f"({abs(percentage_change):.1f}%)** "
        f"compared with the normal scenario."
    )

else:

    st.info(
        "➡️ The selected What-If conditions "
        "produce the same predicted demand "
        "as the normal scenario."
    )