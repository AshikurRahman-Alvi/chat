import secrets
from datetime import datetime, timezone,timedelta
import db
def generate_otp(length=6):
    return ''.join(secrets.choice('0123456789') for _ in range(length))


def save_otp(identifier,otp):
    #otp = generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

    db.otp_collection.update_one(
        {"identifier": identifier},
        {
            "$set": {
                "otp": otp,
                "expires_at": expires_at,
                "created_at": datetime.now(timezone.utc)
            }
        },
        upsert=True
    )

    return otp


from datetime import datetime, timezone

def verify_otp(email, otp):
    record = db.otp_collection.find_one({
        "identifier": email
    })

    if not record:
        return False

    # Check OTP
    stored_otp = str(record["otp"])
    entered_otp = str(otp).strip()

    if stored_otp != entered_otp:
        return False

    # Check expiration
    expires_at = record["expires_at"]

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) > expires_at:
        return False

    return True