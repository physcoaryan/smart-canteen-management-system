import os

from dotenv import load_dotenv
from pymongo import MongoClient, ReturnDocument

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in the .env file")

client = MongoClient(MONGO_URI)

db = client["smart_canteen"]

users_collection = db["users"]
menu_collection = db["menu"]
orders_collection = db["orders"]
token_counters_collection = db["token_counters"]

def get_next_token():

    from datetime import datetime
    from zoneinfo import ZoneInfo

    today = datetime.now(
        ZoneInfo("Asia/Kolkata")
    ).strftime("%Y-%m-%d")

    counter = token_counters_collection.find_one_and_update(
        {"date": today},
        {"$inc": {"number": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )

    token_number = counter["number"]

    return f"SC-{token_number:03d}"

try:
    client.admin.command("ping")
    print("MongoDB connection successful!")
except Exception as e:
    print("MongoDB connection failed:", e)