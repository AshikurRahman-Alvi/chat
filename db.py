from pymongo import MongoClient
from datetime import datetime, timezone
import secrets
import hashlib
import os
from bson import ObjectId
from bson.errors import InvalidId

MONGODB_URL = os.getenv("MONGODB_URL")


client = MongoClient(MONGODB_URL)

db = client["messaging_app"]
user_collection = db["user"]
temp_user_collection = db["temp_user"]
otp_collection = db["otps"]
sessions_collection = db["sessions"]


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

        "connection" : [],

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



def _identifier_query(identifier):
    if "@" in identifier:
        return {"email": identifier}
    return {"phone": identifier}


def transfer_temp_to_user(identifier):
    """Move a verified temp user into the user collection.
    Returns the new user's _id, or None if there's nothing to transfer
    or the account already exists."""
    query = _identifier_query(identifier)

    # Latest signup attempt wins if there are duplicates
    temp = temp_user_collection.find_one(
        query, sort=[("account.created_at", -1)]
    )
    if temp is None:
        return None

    # Already registered: just clean up the temp records
    if user_collection.find_one(query, {"_id": 1}):
        temp_user_collection.delete_many(query)
        return None

    temp.pop("_id")  # let MongoDB create a new _id in the user collection
    now = datetime.now(timezone.utc)
    temp["account"]["email_verified"] = temp["email"] is not None
    temp["account"]["phone_verified"] = temp["phone"] is not None
    temp["account"]["updated_at"] = now

    result = user_collection.insert_one(temp)
    temp_user_collection.delete_many(query)  # remove all attempts for this identifier
    return result.inserted_id


def get_user_id(identifier):
    user = user_collection.find_one(
        {"$or": [{"email": identifier}, {"phone": identifier}]},
        {"_id": 1}
    )
    return str(user["_id"]) if user else None   # str, so it fits in the session


def get_user_by_id(user_id):
    try:
        oid = ObjectId(user_id)
    except (InvalidId, TypeError):
        return None
    return user_collection.find_one({"_id": oid})






def get_user_by_email(email):
    return user_collection.find_one({"email": email}, {"_id": 1})

def update_password(email, password_hash):
    result = user_collection.update_one(
        {"email": email},
        {"$set": {
            "password_hash": password_hash,
            "account.updated_at": datetime.now(timezone.utc)
        }}
    )
    return result.modified_count == 1