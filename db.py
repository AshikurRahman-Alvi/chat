from pymongo import MongoClient
from datetime import datetime, timezone
import hashlib


MONGODB_URL = "mongodb+srv://rominasultana9_db_user:7GYZIXphaUiekxKc@damo.bnbkodq.mongodb.net/?appName=Damo"

client = MongoClient(MONGODB_URL)

db = client["messaging_app"]
user_collection = db["user"]
temp_user_collection = db["temp_user"]
otp_collection = db["otps"]



def is_user_exists_by_email(email):
    user = user_collection.find_one(
        {"email": email},
        {"_id": 1}
    )

    return user is not None


def create_temp_user(first, last, identifier, password_hash,
                day, month, year, gender, custom_gender=None):

    now = datetime.now(timezone.utc)

    # Separate email and phone
    if "@" in identifier:
        email = identifier
        phone = None
    else:
        email = None
        phone = identifier

    # Display name
    display_name = f"{first} {last}"

    user = {
        "_id": None,  # MongoDB creates ObjectId automatically

        "first_name": first,
        "surname": last,

        "email": email,
        "phone": phone,

        "password_hash": password_hash,

        "date_of_birth": {
            "day": int(day),
            "month": int(month),
            "year": int(year)
        },

        "gender": gender,

        "account": {
            "created_at": now,
            "updated_at": now,
            "status": "active",
            "email_verified": False,
            "phone_verified": False
        },

        "profile": {
            "username": None,
            "display_name": display_name,
            "profile_photo": None,
            "bio": ""
        },

        "last_login": None
    }

    # Remove _id so MongoDB generates ObjectId automatically
    user.pop("_id")

    result = temp_user_collection.insert_one(user)

    return result.inserted_id




def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def login(identifier, password):
    # Find user by email or phone
    user = user_collection.find_one({
        "$or": [
            {"email": identifier},
            {"phone": identifier}
        ]
    })

    # User doesn't exist
    if user is None:
        return False

    # Hash entered password
    password_hash = hash_password(password)

    # Check password
    if user["password_hash"] != password_hash:
        return False

    return True