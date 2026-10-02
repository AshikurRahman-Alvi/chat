import smtplib
from email.message import EmailMessage

sender = "xyz.123.verify@gmail.com"
password = "jhamzzhpdnfgxhmr"
receiver = "ashikurrahmanalvi00@gmail.com"

def sent_mail(receiver,otp):
    msg = EmailMessage()
    msg["Subject"] = "Test email"
    msg["From"] = sender
    msg["To"] = receiver
    msg.set_content(f"Your otp is {otp}")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)

    print("Email sent!")