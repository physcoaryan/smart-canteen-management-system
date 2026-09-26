from database import menu_collection


# -------------------------
# LOAD MENU ITEMS
# -------------------------

def get_menu_items():

    menu_items = menu_collection.find(
        {"available": True},
        {
            "_id": 0,
            "item": 1
        }
    )

    return [
        item["item"]
        for item in menu_items
    ]


# -------------------------
# FIND ITEM IN USER QUERY
# -------------------------

def find_item(user_text):

    menu_items = get_menu_items()

    user_text_lower = user_text.lower()

    # Try longest item names first
    menu_items = sorted(
        menu_items,
        key=len,
        reverse=True
    )

    for item in menu_items:

        if item.lower() in user_text_lower:

            return item

    return None