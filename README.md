# Chatify

A messaging web app built with **Flask** and **MongoDB**. It currently supports account sign-up with email OTP verification, login, and a forgot-password page. Real-time messaging is planned.

## Features

- Sign up with email or phone, with date of birth and gender
- Email OTP verification (6-digit code, expires in 5 minutes) sent via [Resend](https://resend.com)
- Login with email or phone and password
- Pending accounts held in a `temp_user` collection until verified, then moved to `user`

## Tech stack

| Part     | Tool                  |
| -------- | --------------------- |
| Backend  | Python, Flask         |
| Database | MongoDB (PyMongo)     |
| Email    | Resend                |
| Frontend | Jinja2 HTML templates |

## Project structure

```
chat/
├── app.py            # Flask app and routes
├── db.py             # MongoDB connection and user functions
├── otp.py            # OTP generation, storage and verification
├── mail.py           # Sends OTP emails via Resend
├── password.py       # Password hashing
├── requirements.txt  # Python dependencies
└── templates/        # HTML pages (login, sign-up, OTP, forgot password, 404, ...)
```

## Getting started

### 1. Clone the repo

```bash
git clone https://github.com/AshikurRahman-Alvi/chat.git
cd chat
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set environment variables

Never commit secrets to the repo. Create a `.env` file (and add it to `.gitignore`) or export these in your shell:

| Variable         | Description                                 |
| ---------------- | ------------------------------------------- |
| `MONGODB_URL`    | MongoDB connection string (e.g. from Atlas) |
| `SECRET_KEY`     | Long random string used to sign sessions    |
| `RESEND_API_KEY` | API key from your Resend account            |

### 4. Run the app

```bash
flask --app app run --debug
```

Open http://127.0.0.1:5000 in your browser.

## Routes

| Route               | Method | Purpose                            |
| ------------------- | ------ | ---------------------------------- |
| `/`                 | GET    | Home / login page                  |
| `/Create_account`   | GET    | Sign-up page                       |
| `/submit_create`    | POST   | Create a pending account, send OTP |
| `/otp`              | GET    | OTP entry page                     |
| `/verify-otp_route` | POST   | Verify the OTP                     |
| `/submit_login`     | POST   | Log in                             |
| `/forgot`           | GET    | Forgot-password page               |
| `/legal`            | GET    | Legal page                         |

## Database collections

Database name: `messaging_app`

- `temp_user`: sign-ups waiting for OTP verification
- `user`: verified accounts
- `otps`: one-time codes with expiry times

## Roadmap

- [ ] Move verified users from `temp_user` to `user`
- [ ] Session-based login and logout
- [ ] Forgot-password flow
- [ ] Message dashboard and inbox
- [ ] Real-time chat with Flask-SocketIO
- [ ] User profiles (username, photo, bio)
- [ ] Rate limiting, CSRF protection and deployment

## License

No license has been added yet.
