from flask import Flask, render_template, request, redirect, session
import db
import password as pd
import requests,mail,otp


app = Flask(__name__)
app.secret_key = "your-secret-key"


@app.route("/")
def home():
    login_error = session.pop("login_error", None)

    return render_template(
        "index.html",
        login_error=login_error
    )



@app.route("/login")
def login():
    return "<h1>login</h1>"

@app.route("/forgot")
def forgot():
    return render_template("forgot_password.html")

@app.route("/submit_login", methods=["POST"])
def submit_login():
    identifier = request.form.get("identifier")
    password = request.form.get("password")



    if db.login(identifier,password):
        return "Login successful"
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

    
    db.temp_user_collection(
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
    print(result)

    # verify OTP here

    if not result:
        return render_template(
            "email_verify.html",
            email=email,
            error="Incorrect OTP. Please try again."
        )

    # OTP is correct
    return redirect("/login")


@app.route("/Create_account")
def Create_account():
    return render_template("create_account.html")

@app.route("/legal")
def legal():
    return render_template("legal.html")

@app.route("/verified")
def legal():
    return render_template("verified.html")


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404
