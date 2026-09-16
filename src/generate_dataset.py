import pandas as pd
import numpy as np

np.random.seed(42)


# --------------------------------------------------
# 1. MENU
# --------------------------------------------------

menu = [
    ("Vada Pav", "Snacks", 20),
    ("Samosa", "Snacks", 15),
    ("Kachori", "Snacks", 20),
    ("Misal Pav", "Snacks", 50),
    ("Bread Pakoda", "Snacks", 25),

    ("Idli", "South Indian", 35),
    ("Medu Vada", "South Indian", 30),
    ("Masala Dosa", "South Indian", 50),
    ("Plain Dosa", "South Indian", 40),
    ("Uttapam", "South Indian", 45),

    ("Roti Sabji", "Meals", 60),
    ("Dal Rice", "Meals", 55),
    ("Veg Thali", "Meals", 80),
    ("Jeera Rice", "Meals", 50),
    ("Paneer Masala", "Meals", 90),

    ("Tea", "Beverages", 12),
    ("Coffee", "Beverages", 20),
    ("Cold Drink", "Beverages", 30),
    ("Lemon Juice", "Beverages", 25),
    ("Buttermilk", "Beverages", 20),

    ("Veg Sandwich", "Fast Food", 40),
    ("Cheese Sandwich", "Fast Food", 55),
    ("Veg Burger", "Fast Food", 60),
    ("Maggi", "Fast Food", 40),
    ("Veg Momos", "Fast Food", 50),
]


# --------------------------------------------------
# 2. BASE DEMAND
# --------------------------------------------------

base_demand = {
    "Vada Pav": 85,
    "Samosa": 70,
    "Kachori": 45,
    "Misal Pav": 40,
    "Bread Pakoda": 35,

    "Idli": 40,
    "Medu Vada": 35,
    "Masala Dosa": 45,
    "Plain Dosa": 30,
    "Uttapam": 25,

    "Roti Sabji": 55,
    "Dal Rice": 45,
    "Veg Thali": 50,
    "Jeera Rice": 35,
    "Paneer Masala": 25,

    "Tea": 110,
    "Coffee": 75,
    "Cold Drink": 60,
    "Lemon Juice": 45,
    "Buttermilk": 50,

    "Veg Sandwich": 40,
    "Cheese Sandwich": 30,
    "Veg Burger": 35,
    "Maggi": 55,
    "Veg Momos": 45
}


# --------------------------------------------------
# 3. DATE RANGE
# --------------------------------------------------

dates = pd.date_range(
    start="2025-07-01",
    end="2026-06-30",
    freq="D"
)


# --------------------------------------------------
# 4. CANTEEN TIME SLOTS
# --------------------------------------------------

# Canteen operating hours:
# 8:00 AM to 5:00 PM
# One slot every 15 minutes

time_slots = pd.date_range(
    start="08:00",
    end="17:00",
    freq="15min"
).time


records = []


# --------------------------------------------------
# 5. GENERATE SALES DATA
# --------------------------------------------------

for date in dates:

    # --------------------------------------------------
    # DAILY INFORMATION
    # --------------------------------------------------

    day_of_week = date.day_name()
    month = date.month

    # Canteen operating pattern
    is_saturday = int(day_of_week == "Saturday")
    is_sunday = int(day_of_week == "Sunday")

    # Sunday:
    # College canteen is completely closed.
    if is_sunday:
        continue


    # --------------------------------------------------
    # COLLEGE HOLIDAYS
    # --------------------------------------------------

    is_holiday = int(
        (date.month == 10 and date.day in range(20, 25))
        or (date.month == 12 and date.day >= 25)
        or (date.month == 1 and date.day <= 2)
        or (date.month == 5 and date.day >= 1)
    )


    # --------------------------------------------------
    # EXAM PERIOD
    # --------------------------------------------------

    is_exam_period = int(
        (date.month in [11, 4])
        and (10 <= date.day <= 25)
    )


    # --------------------------------------------------
    # COLLEGE EVENTS
    # --------------------------------------------------

    is_event = int(
        (date.month == 9 and 10 <= date.day <= 12)
        or (date.month == 2 and 15 <= date.day <= 17)
    )


    # --------------------------------------------------
    # WEATHER
    # --------------------------------------------------

    if month in [6, 7, 8, 9]:

        weather = np.random.choice(
            ["Sunny", "Cloudy", "Rainy"],
            p=[0.25, 0.30, 0.45]
        )

    else:

        weather = np.random.choice(
            ["Sunny", "Cloudy", "Rainy"],
            p=[0.65, 0.25, 0.10]
        )


    # --------------------------------------------------
    # TEMPERATURE
    # --------------------------------------------------

    if month in [4, 5]:

        temperature = np.random.normal(32, 3)

    elif month in [6, 7, 8, 9]:

        temperature = np.random.normal(27, 3)

    else:

        temperature = np.random.normal(25, 3)


    # --------------------------------------------------
    # RAINFALL
    # --------------------------------------------------

    if weather == "Rainy":

        rainfall = np.random.uniform(10, 50)

    elif weather == "Cloudy":

        rainfall = np.random.uniform(0, 10)

    else:

        rainfall = 0


    # --------------------------------------------------
    # TIME SLOTS
    # --------------------------------------------------

    for time_slot in time_slots:


        # --------------------------------------------------
        # MENU ITEMS
        # --------------------------------------------------

        for item, category, price in menu:

            # Start with normal demand
            demand = base_demand[item]

            # --------------------------------------------------
            # TIME-OF-DAY EFFECT
            # --------------------------------------------------

            time_str = time_slot.strftime("%H:%M")

            if time_str == "10:30":
                demand *= 1.5

            elif time_str in ["12:45", "13:00", "13:15"]:
                demand *= 1.5

            else:
                demand *= 0.4


            # --------------------------------------------------
            # SATURDAY EFFECT
            # --------------------------------------------------

            # College is mostly off on Saturday.
            # Only hostel students and a few others
            # are expected to use the canteen.

            if is_saturday:

                demand *= 0.35


            # --------------------------------------------------
            # HOLIDAY EFFECT
            # --------------------------------------------------

            if is_holiday:

                demand *= 0.15


            # --------------------------------------------------
            # EXAM EFFECT
            # --------------------------------------------------

            if is_exam_period:

                if item in ["Tea", "Coffee", "Maggi"]:

                    demand *= 1.35

                else:

                    demand *= 1.10


            # --------------------------------------------------
            # COLLEGE EVENT EFFECT
            # --------------------------------------------------

            if is_event:

                demand *= 1.40


            # --------------------------------------------------
            # WEATHER EFFECT
            # --------------------------------------------------

            if weather == "Rainy":

                if item in [
                    "Vada Pav",
                    "Samosa",
                    "Kachori",
                    "Tea",
                    "Coffee",
                    "Maggi"
                ]:

                    demand *= 1.40

                elif item in [
                    "Cold Drink",
                    "Lemon Juice"
                ]:

                    demand *= 0.70


            elif weather == "Sunny":

                if item in [
                    "Cold Drink",
                    "Lemon Juice",
                    "Buttermilk"
                ]:

                    demand *= 1.35


            # --------------------------------------------------
            # RANDOM VARIATION
            # --------------------------------------------------

            quantity = np.random.normal(
                demand,
                max(demand * 0.12, 2)
            )

            quantity = max(
                0,
                round(quantity)
            )


            # --------------------------------------------------
            # REVENUE
            # --------------------------------------------------

            revenue = quantity * price


            # --------------------------------------------------
            # STORE RECORD
            # --------------------------------------------------

            records.append([
                date,
                time_slot,
                day_of_week,
                month,
                item,
                category,
                price,
                quantity,
                revenue,
                is_saturday,
                is_sunday,
                is_exam_period,
                is_holiday,
                weather,
                round(temperature, 2),
                round(rainfall, 2),
                is_event
            ])


# --------------------------------------------------
# 6. CREATE DATAFRAME
# --------------------------------------------------

columns = [
    "date",
    "time_slot",
    "day_of_week",
    "month",
    "item",
    "category",
    "price",
    "quantity_sold",
    "revenue",
    "is_saturday",
    "is_sunday",
    "is_exam_period",
    "is_holiday",
    "weather",
    "temperature",
    "rainfall",
    "college_event"
]


df = pd.DataFrame(
    records,
    columns=columns
)


# --------------------------------------------------
# 7. SAVE DATASET
# --------------------------------------------------

df.to_csv(
    "data/canteen_sales.csv",
    index=False
)


# --------------------------------------------------
# 8. BASIC INFORMATION
# --------------------------------------------------

print("Dataset generated successfully!")
print()

print("Shape:", df.shape)
print()

print("First 5 rows:")
print(df.head())
print()

print("Total Revenue:", df["revenue"].sum())
print()

print("Total Quantity Sold:", df["quantity_sold"].sum())