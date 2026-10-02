import smtplib
from email.message import EmailMessage

sender = "xyz.123.verify@gmail.com"
password = "jhamzzhpdnfgxhmr"

def sent_mail(receiver, otp):
    msg = EmailMessage()
    msg["Subject"] = "Test email"
    msg["From"] = sender
    msg["To"] = receiver
    msg.set_content(f"Your OTP is {otp}")

    try:
        print("Connecting to Gmail...")

        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465,
            timeout=15
        ) as smtp:

            print("Connected to Gmail")

            smtp.login(sender, password)

            print("Logged in to Gmail")

            smtp.send_message(msg)

            print("Email sent!")

        return True

    except Exception as e:
        print("Email error:", repr(e))
        return False
