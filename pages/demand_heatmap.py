import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.interpolate import make_interp_spline


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Canteen Analytics",
    page_icon="📊",
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
    "📊 Canteen Analytics"
)

st.write(
    "Explore predicted food demand, peak periods, "
    "food trends, category distribution, and model "
    "performance for a selected date."
)

st.divider()


# =====================================================
# DATE SELECTION
# =====================================================

st.subheader(
    "📅 Select Date"
)

selected_date = st.date_input(
    "Choose a date"
)

selected_date = pd.Timestamp(
    selected_date
)


# =====================================================
# FIND HISTORICAL DATA
# =====================================================

date_data = df[
    df["date"] == selected_date
]


if date_data.empty:

    st.warning(
        "No historical data is available for "
        f"**{selected_date.strftime('%d %B %Y')}**."
    )

    st.stop()


# =====================================================
# DATE CONDITIONS
# =====================================================

day_of_week = date_data[
    "day_of_week"
].iloc[0]

month = int(
    date_data["month"].iloc[0]
)

is_saturday = int(
    date_data["is_saturday"].iloc[0]
)

is_sunday = int(
    date_data["is_sunday"].iloc[0]
)

is_exam_period = int(
    date_data["is_exam_period"].iloc[0]
)

is_holiday = int(
    date_data["is_holiday"].iloc[0]
)

weather = (
    date_data["weather"]
    .mode()
    .iloc[0]
)

college_event = (
    date_data["college_event"]
    .mode()
    .iloc[0]
)


# =====================================================
# SHOW DATE CONDITIONS
# =====================================================

st.subheader(
    "📌 Conditions for Selected Date"
)

condition_col1, condition_col2, condition_col3, condition_col4 = (
    st.columns(4)
)


with condition_col1:

    st.metric(
        "Day",
        day_of_week
    )


with condition_col2:

    st.metric(
        "Weather",
        weather
    )


with condition_col3:

    st.metric(
        "Exam",
        "Yes" if is_exam_period == 1 else "No"
    )


with condition_col4:

    st.metric(
        "Holiday",
        "Yes" if is_holiday == 1 else "No"
    )


event_col1, event_col2 = st.columns(2)


with event_col1:

    event_label = (
        "Yes"
        if str(college_event).lower()
        in ["1", "yes", "true"]
        else "No"
    )

    st.metric(
        "College Event",
        event_label
    )


with event_col2:

    st.metric(
        "Selected Date",
        selected_date.strftime(
            "%d %b %Y"
        )
    )


st.divider()


# =====================================================
# FOOD ITEM SELECTION
# =====================================================

st.subheader(
    "🍴 Food Items"
)

selected_items = st.multiselect(
    "Select food items to display",
    sorted(
        df["item"].unique()
    ),
    default=sorted(
        df["item"].unique()
    )
)


if not selected_items:

    st.info(
        "Please select at least one food item."
    )

    st.stop()


# =====================================================
# TIME SLOTS
# =====================================================

time_slots = sorted(
    df["time_slot"].unique()
)


# =====================================================
# GENERATE PREDICTIONS
# =====================================================

predictions = []


for food_item in selected_items:

    # -------------------------------------------------
    # Get item information
    # -------------------------------------------------

    item_info = df[
        df["item"] == food_item
    ].iloc[0]

    category = item_info["category"]
    price = item_info["price"]


    # -------------------------------------------------
    # Generate prediction for every time slot
    # -------------------------------------------------

    for current_time in time_slots:

        hour = current_time.hour
        minute = current_time.minute

        time_index = (
            hour * 60
            + minute
        )


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


# =====================================================
# CREATE PREDICTION DATAFRAME
# =====================================================

prediction_df = pd.DataFrame(
    predictions
)


# =====================================================
# CREATE HEATMAP TABLE
# =====================================================

heatmap_data = (
    prediction_df
    .pivot(
        index="item",
        columns="time",
        values="prediction"
    )
)


# =====================================================
# VISUAL DEMAND HEATMAP
# =====================================================

st.subheader(
    "🔥 Predicted Demand Heatmap"
)

st.write(
    "Darker cells indicate higher predicted demand."
)


fig, ax = plt.subplots(
    figsize=(18, 8)
)


sns.heatmap(
    heatmap_data,
    annot=True,
    fmt=".0f",
    cmap="YlOrRd",
    linewidths=0.3,
    linecolor="white",
    cbar_kws={
        "label": "Predicted Demand (Units)"
    },
    ax=ax
)


ax.set_xlabel(
    "Time"
)

ax.set_ylabel(
    "Food Item"
)

ax.set_title(
    f"Predicted Canteen Demand — "
    f"{selected_date.strftime('%d %B %Y')}"
)


plt.xticks(
    rotation=45,
    ha="right"
)

plt.yticks(
    rotation=0
)

plt.tight_layout()


st.pyplot(
    fig,
    use_container_width=True
)

plt.close(fig)


# =====================================================
# DEMAND TREND CHART
# =====================================================

st.divider()

st.subheader(
    "📈 Demand Trend by Time"
)

st.write(
    "View how predicted demand changes throughout "
    "the day for selected food items."
)


# =====================================================
# SELECT ITEMS FOR TREND CHART
# =====================================================

trend_items = st.multiselect(
    "Select food items for trend analysis",
    options=selected_items,
    default=selected_items[:3],
    key="trend_items"
)


if not trend_items:

    st.info(
        "Please select at least one food item "
        "to display the demand trend."
    )

else:

    # =================================================
    # PREPARE TREND DATA
    # =================================================

    trend_data = prediction_df[
        prediction_df["item"].isin(trend_items)
    ].copy()


    # Convert time into numerical minutes

    trend_data["time_minutes"] = (
        pd.to_datetime(
            trend_data["time"],
            format="%H:%M"
        ).dt.hour * 60
        +
        pd.to_datetime(
            trend_data["time"],
            format="%H:%M"
        ).dt.minute
    )


    # Sort chronologically

    trend_data = trend_data.sort_values(
        "time_minutes"
    )


    # =================================================
    # CALCULATE AVERAGE DEMAND
    # =================================================

    average_demand = (
        trend_data
        .groupby("time_minutes")["prediction"]
        .mean()
        .reset_index()
    )


    # =================================================
    # CREATE TREND CHART
    # =================================================

    fig, ax = plt.subplots(
        figsize=(15, 6)
    )


    # =================================================
    # PLOT EACH SELECTED FOOD ITEM
    # =================================================

    for item in trend_items:

        item_data = trend_data[
            trend_data["item"] == item
        ].sort_values(
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
                linewidth=2,
                marker="o",
                label=item
            )


        # ---------------------------------------------
        # Show prediction points
        # ---------------------------------------------

        ax.scatter(
            x,
            y,
            s=25
        )


    # =================================================
    # PLOT AVERAGE DEMAND
    # =================================================

    avg_x = (
        average_demand[
            "time_minutes"
        ].values
    )

    avg_y = (
        average_demand[
            "prediction"
        ].values
    )


    if len(avg_x) >= 4:

        avg_spline = make_interp_spline(
            avg_x,
            avg_y,
            k=3
        )


        avg_x_smooth = np.linspace(
            avg_x.min(),
            avg_x.max(),
            300
        )


        avg_y_smooth = avg_spline(
            avg_x_smooth
        )


        avg_y_smooth = np.maximum(
            avg_y_smooth,
            0
        )


        ax.plot(
            avg_x_smooth,
            avg_y_smooth,
            linestyle="--",
            linewidth=3,
            label="Average Demand"
        )

    else:

        ax.plot(
            avg_x,
            avg_y,
            linestyle="--",
            linewidth=3,
            label="Average Demand"
        )


    # =================================================
    # FORMAT X-AXIS
    # =================================================

    unique_times = sorted(
        trend_data[
            "time_minutes"
        ].unique()
    )


    time_labels = [
        f"{int(t // 60):02d}:{int(t % 60):02d}"
        for t in unique_times
    ]


    ax.set_xticks(
        unique_times
    )


    ax.set_xticklabels(
        time_labels,
        rotation=45,
        ha="right"
    )


    # =================================================
    # CHART LABELS
    # =================================================

    ax.set_xlabel(
        "Time"
    )

    ax.set_ylabel(
        "Predicted Demand (Units)"
    )

    ax.set_title(
        f"Predicted Demand Trend — "
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


# =====================================================
# TOP 5 FOOD ITEMS
# =====================================================

st.divider()

st.subheader(
    "📊 Top 5 Food Items by Predicted Demand"
)

st.write(
    "The five food items with the highest total "
    "predicted demand for the selected date."
)


# -----------------------------------------------------
# Calculate total predicted demand per item
# -----------------------------------------------------

top_items_data = (
    prediction_df
    .groupby("item")["prediction"]
    .sum()
    .sort_values(
        ascending=False
    )
    .head(5)
    .sort_values(
        ascending=True
    )
)


# -----------------------------------------------------
# Create horizontal bar chart
# -----------------------------------------------------

fig, ax = plt.subplots(
    figsize=(12, 5)
)


ax.barh(
    top_items_data.index,
    top_items_data.values
)


ax.set_xlabel(
    "Total Predicted Demand (Units)"
)

ax.set_ylabel(
    "Food Item"
)

ax.set_title(
    "Top 5 Food Items by Total Predicted Demand"
)


# Add values at the end of bars

for index, value in enumerate(
    top_items_data.values
):

    ax.text(
        value,
        index,
        f" {int(value)}",
        va="center"
    )


ax.grid(
    axis="x",
    alpha=0.25
)


plt.tight_layout()


st.pyplot(
    fig,
    use_container_width=True
)

plt.close(fig)


# =====================================================
# HOURLY DEMAND + CATEGORY DISTRIBUTION
# =====================================================

st.divider()

st.subheader(
    "📈 Demand Overview"
)

st.write(
    "Compare overall demand throughout the day "
    "with the distribution of demand across food categories."
)


hourly_col, category_col = st.columns(
    2
)


# =====================================================
# LEFT — HOURLY TOTAL DEMAND
# =====================================================

with hourly_col:

    st.markdown(
        "#### 📈 Hourly Total Demand"
    )

    # ---------------------------------------------
    # Convert time into minutes
    # ---------------------------------------------

    hourly_data = prediction_df.copy()

    hourly_data["time_minutes"] = (
        pd.to_datetime(
            hourly_data["time"],
            format="%H:%M"
        ).dt.hour * 60
        +
        pd.to_datetime(
            hourly_data["time"],
            format="%H:%M"
        ).dt.minute
    )


    # ---------------------------------------------
    # Aggregate all selected food items
    # ---------------------------------------------

    hourly_demand = (
        hourly_data
        .groupby("time_minutes")["prediction"]
        .sum()
        .reset_index()
    )


    # ---------------------------------------------
    # Create small line graph
    # ---------------------------------------------

    fig, ax = plt.subplots(
        figsize=(8, 4.5)
    )


    x = hourly_demand[
        "time_minutes"
    ].values

    y = hourly_demand[
        "prediction"
    ].values


    # ---------------------------------------------
    # Smooth curve when possible
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
            250
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
            linewidth=2
        )

    else:

        ax.plot(
            x,
            y,
            linewidth=2,
            marker="o"
        )


    # ---------------------------------------------
    # Time labels
    # ---------------------------------------------

    unique_hour_times = sorted(
        hourly_demand[
            "time_minutes"
        ].unique()
    )


    hour_labels = [
        f"{int(t // 60):02d}:{int(t % 60):02d}"
        for t in unique_hour_times
    ]


    ax.set_xticks(
        unique_hour_times
    )


    ax.set_xticklabels(
        hour_labels,
        rotation=45,
        ha="right"
    )


    ax.set_xlabel(
        "Time"
    )

    ax.set_ylabel(
        "Total Predicted Demand"
    )

    ax.set_title(
        "Total Demand Throughout the Day"
    )


    ax.grid(
        alpha=0.25
    )


    plt.tight_layout()


    st.pyplot(
        fig,
        use_container_width=True
    )

    plt.close(fig)


# =====================================================
# RIGHT — CATEGORY DISTRIBUTION
# =====================================================

with category_col:

    st.markdown(
        "#### 🍩 Demand Distribution by Category"
    )

    # ---------------------------------------------
    # Calculate category demand
    # ---------------------------------------------

    category_demand = (
        prediction_df
        .groupby("category")["prediction"]
        .sum()
        .sort_values(
            ascending=False
        )
    )


    # ---------------------------------------------
    # Create donut chart
    # ---------------------------------------------

    fig, ax = plt.subplots(
        figsize=(8, 4.5)
    )


    wedges, texts, autotexts = ax.pie(
        category_demand.values,
        labels=category_demand.index,
        autopct="%1.1f%%",
        startangle=90,
        wedgeprops={
            "width": 0.42
        }
    )


    ax.set_title(
        "Predicted Demand by Food Category"
    )


    # Keep chart circular

    ax.axis(
        "equal"
    )


    plt.tight_layout()


    st.pyplot(
        fig,
        use_container_width=True
    )

    plt.close(fig)


# =====================================================
# PREDICTED VS ACTUAL DEMAND
# =====================================================

st.divider()

st.subheader(
    "🔎 Predicted vs Actual Demand"
)

st.write(
    "Compare the model's predicted demand with the "
    "actual demand recorded for the selected date."
)


# =====================================================
# ACTUAL DEMAND FOR SELECTED DATE
# =====================================================

actual_data = date_data[
    date_data["item"].isin(selected_items)
].copy()


actual_data["time"] = actual_data[
    "time_slot"
].apply(
    lambda x: x.strftime("%H:%M")
)


actual_table = (
    actual_data
    .pivot(
        index="item",
        columns="time",
        values="quantity_sold"
    )
)


# =====================================================
# ALIGN PREDICTIONS AND ACTUAL VALUES
# =====================================================

common_items = (
    heatmap_data.index
    .intersection(actual_table.index)
)

common_times = (
    heatmap_data.columns
    .intersection(actual_table.columns)
)


predicted_compare = heatmap_data.loc[
    common_items,
    common_times
]

actual_compare = actual_table.loc[
    common_items,
    common_times
]


# =====================================================
# CALCULATE DIFFERENCE
# =====================================================

difference = (
    predicted_compare
    - actual_compare
)


# =====================================================
# SUMMARY METRICS
# =====================================================

mae = (
    difference.abs()
    .mean()
    .mean()
)


rmse = (
    (difference ** 2)
    .mean()
    .mean()
) ** 0.5


metric_col1, metric_col2 = st.columns(2)


with metric_col1:

    st.metric(
        "Average Absolute Error",
        f"{mae:.2f} units"
    )


with metric_col2:

    st.metric(
        "RMSE",
        f"{rmse:.2f} units"
    )


# =====================================================
# SELECT ITEM FOR DETAILED COMPARISON
# =====================================================

comparison_item = st.selectbox(
    "🍴 Select Food Item",
    common_items,
    key="comparison_item"
)


# =====================================================
# SELECTED ITEM METRICS
# =====================================================

selected_item_difference = (
    difference.loc[comparison_item]
)


item_mae = (
    selected_item_difference
    .abs()
    .mean()
)


item_rmse = (
    (
        selected_item_difference ** 2
    )
    .mean()
) ** 0.5


st.markdown(
    f"### 🍴 {comparison_item} Performance"
)


item_metric_col1, item_metric_col2 = st.columns(2)


with item_metric_col1:

    st.metric(
        "Item MAE",
        f"{item_mae:.2f} units"
    )


with item_metric_col2:

    st.metric(
        "Item RMSE",
        f"{item_rmse:.2f} units"
    )


comparison_df = pd.DataFrame(
    {
        "Time": common_times,
        "Actual Demand": actual_compare.loc[
            comparison_item,
            common_times
        ].values,
        "Predicted Demand": predicted_compare.loc[
            comparison_item,
            common_times
        ].values
    }
)


comparison_df["Difference"] = (
    comparison_df["Predicted Demand"]
    - comparison_df["Actual Demand"]
)


# =====================================================
# DISPLAY COMPARISON
# =====================================================

st.dataframe(
    comparison_df,
    use_container_width=True,
    hide_index=True
)