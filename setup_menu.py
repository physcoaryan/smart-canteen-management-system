import pandas as pd

from database import menu_collection


# Load the existing dataset
df = pd.read_csv("data/canteen_sales.csv")


# Create a clean menu from unique items
menu = (
    df[["item", "category", "price"]]
    .drop_duplicates(subset=["item"])
    .reset_index(drop=True)
)


# Convert to MongoDB-friendly records
menu_records = []

for index, row in menu.iterrows():
    menu_records.append({
        "item_id": index + 1,
        "item": row["item"],
        "category": row["category"],
        "price": row["price"],
        "available": True
    })


# Insert only if menu is empty
if menu_collection.count_documents({}) == 0:

    menu_collection.insert_many(menu_records)

    print(
        f"{len(menu_records)} menu items added successfully."
    )

else:

    print("Menu collection already contains data.")