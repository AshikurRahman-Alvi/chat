import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")

sender = "chat <onboarding@resend.dev>"


def sent_mail(receiver, otp):
    try:
        print("Sending OTP email...")

        params = {
            "from": sender,
            "to": [receiver],
            "subject": "Your OTP Code",
            "text": f"Your OTP is {otp}\n\nThis OTP will expire in 5 minutes."
        }

        response = resend.Emails.send(params)

        print("Email sent successfully!")
        print(response)

        return True

    except Exception as e:
        print("Email error:", repr(e))
        return False