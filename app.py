from flask import Flask, render_template, request, redirect, session
from datetime import timedelta
import db
import password as pd
import requests,mail,otp
import os


app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]
app.permanent_session_lifetime = timedelta(days=30)


@app.route("/")
def home():

    user_id = session.get("user_id")

    if not user_id:
        
        login_error = session.pop("login_error", None)
        return render_template(
            "index.html",
            login_error=login_error
        )
    else:
        # Get logged-in user's data
        user = db.get_user_by_id(user_id)

        # User ID is invalid or user no longer exists
        if not user:
            session.clear()

            return redirect("/")

        # User is logged in
        return render_template(
            "inbox.html",
            user=user
        )




@app.route("/login")
def login():
    return render_template("inbox.html")

@app.route("/forgot")
def forgot():
    return render_template("forgot_password.html")

@app.route("/submit_login", methods=["POST"])
def submit_login():
    identifier = request.form.get("identifier")
    password = request.form.get("password")

    if db.login(identifier,password):

        session.permanent = True
        session["user_id"] = db.get_user_id(identifier)

        return redirect("/")
    else:
        session["login_error"] = "Incorrect email or password."
        return redirect("/")


@app.route("/submit_create", methods=["POST"])
def submit_create():

    first = request.form.get("first")
    last = request.form.get("last")
    identifier = request.form.get("identifier")
    password = request.form.get("password")

    day = request.form.get("day")
    month = request.form.get("month")
    year = request.form.get("year")

    gender = request.form.get("gender")
    custom_gender = request.form.get("custom_gender")

    #is_user_e = db.is_user_exists_by_email(identifier)

    
    db.create_temp_user(
        first=first,
        last=last,
        identifier=identifier,
        password_hash=pd.hash_password(password),
        day=day,
        month=month,
        year=year,
        gender=gender
        )
    
    
    code = otp.generate_otp()
    otp.save_otp(identifier, code)
    mail.sent_mail(identifier, code)
    return redirect("/otp?email=" + identifier)


@app.route("/otp")
def otp_page():
    email = request.args.get("email")

    return render_template(
        "email_verify.html",
        email=email
    )

@app.route("/verify-otp_route", methods=["POST"])
def verify_otp_route():
    email = request.form.get("email")
    otps = request.form.get("otp")

   

    result = otp.verify_otp(email,otps)
    #print(result)

    # verify OTP here

    if not result:
        return render_template(
            "email_verify.html",
            email=email,
            error="Incorrect OTP. Please try again."
        )
    else:
        user_id = db.transfer_temp_to_user(email)
        db.otp_collection.delete_one({"identifier": email})  # OTP can't be reused

        if user_id is None:
            return render_template(
                "email_verify.html",
                email=email,
                error="Account could not be created. Please sign up again."
            )

        # OTP is correct
        return redirect("/verified")


@app.route("/Create_account")
def Create_account():
    return render_template("create_account.html")

@app.route("/legal")
def legal():
    return render_template("legal.html")

@app.route("/verified")
def verified():
    return render_template("verified.html")


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404










@app.route("/forgot-submit", methods=["POST"])
def forgot_submit():
    email = (request.form.get("email") or "").strip().lower()

    # Same response whether or not the account exists (prevents email enumeration)
    if db.get_user_by_email(email):
        code = otp.generate_otp()
        otp.save_otp("reset:" + email, code)
        mail.sent_reset_mail(email, code)

    return redirect("/forgot-verify?email=" + email)


@app.route("/forgot-verify")
def forgot_verify():
    return render_template("forgot_verify.html", email=request.args.get("email"))


@app.route("/forgot-verify-submit", methods=["POST"])
def forgot_verify_submit():
    email = (request.form.get("email") or "").strip().lower()
    code = request.form.get("otp")

    if not otp.verify_otp("reset:" + email, code):
        return render_template("forgot_verify.html", email=email,
                               error="Incorrect or expired code.")

    db.otp_collection.delete_one({"identifier": "reset:" + email})  # one-time use
    session["reset_email"] = email                                  # proves OTP passed
    return redirect("/reset-password")


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    email = session.get("reset_email")
    if not email:
        return redirect("/forgot")

    if request.method == "POST":
        new = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        if len(new) < 8:
            return render_template("reset_password.html", error="Use at least 8 characters.")
        if new != confirm:
            return render_template("reset_password.html", error="Passwords don't match.")

        db.update_password(email, pd.hash_password(new))
        session.pop("reset_email", None)
        session["login_error"] = "Password updated. Please log in."
        return redirect("/")

    return render_template("reset_password.html")





@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")