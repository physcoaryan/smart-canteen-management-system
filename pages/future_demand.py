import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Future Demand Prediction",
    page_icon="🔮",
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

    data["date"] = pd.to_datetime(
        data["date"]
    )

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
    "🔮 Future Demand Prediction"
)

st.write(
    "Predict the expected food demand for a future date "
    "using the trained machine learning model."
)

st.divider()


# =====================================================
# FUTURE DATE
# =====================================================

st.subheader(
    "📅 Select Future Date"
)

today = pd.Timestamp.today().normalize()

selected_date = st.date_input(
    "Choose a date",
    min_value=today + pd.Timedelta(days=1),
    value=today + pd.Timedelta(days=1)
)

selected_date = pd.Timestamp(
    selected_date
)


# =====================================================
# FOOD ITEM SELECTION
# =====================================================

st.subheader(
    "🍴 Select Food Items"
)

selected_items = st.multiselect(
    "Select the food items for which you want to predict demand",
    options=sorted(
        df["item"].unique()
    ),
    default=[],
    key="future_items"
)


if not selected_items:

    st.info(
        "Select at least one food item to continue."
    )

    st.stop()


# =====================================================
# FUTURE DATE FEATURES
# =====================================================

day_of_week = selected_date.day_name()

month = selected_date.month

is_saturday = int(
    selected_date.dayofweek == 5
)

is_sunday = int(
    selected_date.dayofweek == 6
)


# =====================================================
# FUTURE CONDITIONS
# =====================================================

st.subheader(
    "🌦️ Future Conditions"
)

condition_col1, condition_col2 = st.columns(2)


with condition_col1:

    weather = st.selectbox(
        "Weather",
        options=sorted(
            df["weather"]
            .dropna()
            .unique()
        )
    )


with condition_col2:

    college_event = st.selectbox(
        "College Event",
        options=sorted(
            df["college_event"]
            .dropna()
            .unique()
        )
    )


condition_col3, condition_col4 = st.columns(2)


with condition_col3:

    is_exam_period = st.selectbox(
        "Exam Period",
        options=[0, 1],
        format_func=lambda x:
            "Yes" if x == 1 else "No"
    )


with condition_col4:

    is_holiday = st.selectbox(
        "Holiday",
        options=[0, 1],
        format_func=lambda x:
            "Yes" if x == 1 else "No"
    )


# =====================================================
# DATE INFORMATION
# =====================================================

st.subheader(
    "📌 Selected Date Information"
)

info_col1, info_col2, info_col3, info_col4 = st.columns(4)


with info_col1:

    st.metric(
        "Date",
        selected_date.strftime(
            "%d %b %Y"
        )
    )


with info_col2:

    st.metric(
        "Day",
        day_of_week
    )


with info_col3:

    st.metric(
        "Saturday",
        "Yes" if is_saturday else "No"
    )


with info_col4:

    st.metric(
        "Sunday",
        "Yes" if is_sunday else "No"
    )


st.divider()


# =====================================================
# PREDICT BUTTON
# =====================================================

predict_button = st.button(
    "🤖 Predict Future Demand",
    type="primary",
    use_container_width=True
)


if predict_button:

    # =================================================
    # GENERATE PREDICTIONS
    # =================================================

    predictions = []


    for food_item in selected_items:

        # ---------------------------------------------
        # Get item information
        # ---------------------------------------------

        item_info = df[
            df["item"] == food_item
        ].iloc[0]

        category = item_info["category"]

        price = item_info["price"]


        # ---------------------------------------------
        # Predict for every available time slot
        # ---------------------------------------------

        for current_time in sorted(
            df["time_slot"].unique()
        ):

            hour = current_time.hour

            minute = current_time.minute

            time_index = (
                hour * 60
                + minute
            )


            # -----------------------------------------
            # Create model input
            # -----------------------------------------

            input_data = pd.DataFrame([
                {
                    "day_of_week": day_of_week,
                    "month": month,
                    "item": food_item,
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


            # -----------------------------------------
            # Model prediction
            # -----------------------------------------

            prediction = model.predict(
                input_data
            )[0]


            prediction = max(
                0,
                round(prediction)
            )


            predictions.append(
                {
                    "item": food_item,
                    "category": category,
                    "time": current_time.strftime(
                        "%H:%M"
                    ),
                    "prediction": prediction
                }
            )


    # =================================================
    # CREATE PREDICTION DATAFRAME
    # =================================================

    prediction_df = pd.DataFrame(
        predictions
    )


    # =================================================
    # RESULTS HEADER
    # =================================================

    st.divider()

    st.subheader(
        "📊 Predicted Future Demand"
    )

    st.write(
        f"Predicted demand for "
        f"**{selected_date.strftime('%d %B %Y')}**"
    )


    # =================================================
    # TOTAL DEMAND PER ITEM
    # =================================================

    item_totals = (
        prediction_df
        .groupby("item")["prediction"]
        .sum()
        .sort_values(
            ascending=False
        )
    )


    # =================================================
    # METRIC CARDS
    # =================================================

    metric_columns = st.columns(
        len(selected_items)
    )


    for column, item in zip(
        metric_columns,
        item_totals.index
    ):

        with column:

            st.metric(
                item,
                f"{int(item_totals[item])} units"
            )


    st.divider()


    # =================================================
    # PREDICTION TABLE
    # =================================================

    st.subheader(
        "📋 Time-wise Prediction"
    )


    prediction_table = (
        prediction_df
        .pivot(
            index="item",
            columns="time",
            values="prediction"
        )
    )


    st.dataframe(
        prediction_table,
        use_container_width=True
    )


    # =================================================
    # DEMAND TREND
    # =================================================

    st.subheader(
        "📈 Predicted Demand Throughout the Day"
    )


    fig, ax = plt.subplots(
        figsize=(15, 6)
    )


    for item in selected_items:

        item_data = prediction_df[
            prediction_df["item"] == item
        ].copy()


        # ---------------------------------------------
        # Convert time to minutes
        # ---------------------------------------------

        item_data["time_minutes"] = (
            pd.to_datetime(
                item_data["time"],
                format="%H:%M"
            ).dt.hour * 60
            +
            pd.to_datetime(
                item_data["time"],
                format="%H:%M"
            ).dt.minute
        )


        item_data = item_data.sort_values(
            "time_minutes"
        )


        x = item_data[
            "time_minutes"
        ].values

        y = item_data[
            "prediction"
        ].values


        # ---------------------------------------------
        # Smooth curve
        # ---------------------------------------------

        if len(x) >= 4:

            spline = make_interp_spline(
                x,
                y,
                k=3
            )


            x_smooth = np.linspace(
                x.min(),
                x.max(),
                300
            )


            y_smooth = spline(
                x_smooth
            )


            y_smooth = np.maximum(
                y_smooth,
                0
            )


            ax.plot(
                x_smooth,
                y_smooth,
                linewidth=2,
                label=item
            )

        else:

            ax.plot(
                x,
                y,
                marker="o",
                linewidth=2,
                label=item
            )


        # ---------------------------------------------
        # Prediction points
        # ---------------------------------------------

        ax.scatter(
            x,
            y,
            s=25
        )


    # =================================================
    # FORMAT TIME AXIS
    # =================================================

    unique_times = sorted(
        prediction_df[
            "time"
        ].unique()
    )


    time_minutes = [
        int(t.split(":")[0]) * 60
        + int(t.split(":")[1])
        for t in unique_times
    ]


    ax.set_xticks(
        time_minutes
    )


    ax.set_xticklabels(
        unique_times,
        rotation=45,
        ha="right"
    )


    ax.set_xlabel(
        "Time"
    )

    ax.set_ylabel(
        "Predicted Demand (Units)"
    )

    ax.set_title(
        f"Future Demand Prediction — "
        f"{selected_date.strftime('%d %B %Y')}"
    )


    ax.grid(
        alpha=0.25
    )


    ax.legend(
        title="Food Items"
    )


    plt.tight_layout()


    st.pyplot(
        fig,
        use_container_width=True
    )

    plt.close(fig)


    # =================================================
    # PEAK DEMAND
    # =================================================

    st.divider()

    st.subheader(
        "🔥 Peak Predicted Demand"
    )


    peak_col1, peak_col2 = st.columns(2)


    # -------------------------------------------------
    # Overall peak
    # -------------------------------------------------

    overall_peak = prediction_df.loc[
        prediction_df["prediction"].idxmax()
    ]


    with peak_col1:

        st.metric(
            "Highest Predicted Demand",
            f"{int(overall_peak['prediction'])} units"
        )

        st.write(
            f"**{overall_peak['item']}** "
            f"at **{overall_peak['time']}**"
        )


    # -------------------------------------------------
    # Total predicted demand
    # -------------------------------------------------

    total_predicted_demand = (
        prediction_df["prediction"]
        .sum()
    )


    with peak_col2:

        st.metric(
            "Total Predicted Demand",
            f"{int(total_predicted_demand)} units"
        )


    # =================================================
    # PREPARATION RECOMMENDATIONS
    # =================================================

    st.divider()

    st.subheader(
        "💡 Preparation Recommendations"
    )


    recommendation_df = (
        prediction_df
        .groupby("item")["prediction"]
        .max()
        .sort_values(
            ascending=False
        )
    )


    for item, demand in recommendation_df.items():

        st.write(
            f"🍴 **{item}** — "
            f"Prepare approximately **{int(demand)} units** "
            f"for its peak demand period."
        )