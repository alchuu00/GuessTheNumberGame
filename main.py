import hashlib
import random
import os
import uuid

from flask import Flask, render_template, request, make_response, redirect, url_for
from sqla_wrapper import SQLAlchemy

app = Flask(__name__)
db_url = os.getenv("DATABASE_URL", "sqlite:///db.sqlite").replace("postgres://", "postgresql://", 1)
db = SQLAlchemy(db_url)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    secret_num = db.Column(db.Integer, unique=False)
    session_token = db.Column(db.String)


db.create_all()


@app.route("/", methods=["GET"])
def index():
    session_token = request.cookies.get("session_token")

    if session_token:
        user = db.query(User).filter_by(session_token=session_token).first()
    else:
        user = None

    return render_template("index.html", user=user)


@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("user-name")
    email = request.form.get("user-email")
    password = request.form.get("user-password")

    salt = "qiz2376rt29"
    # added salt to the password using random string
    hashed_password = hashlib.sha256(salt.encode() + password.encode()).hexdigest()

    secret_num = int(random.randint(1, 30))

    # see if user already exists
    user = db.query(User).filter_by(email=email).first()

    # create a User object
    if not user:
        user = User(name=name, email=email, secret_num=secret_num, password=hashed_password)
        user.save()  # save user into the database

    if hashed_password != user.password:
        return "WRONG PASSWORD! Go back and try again."
    elif hashed_password == user.password:
        # create a random session token for this user
        session_token = str(uuid.uuid4())

        # save the session token in a database
        user.session_token = session_token
        user.save()

        # save user's session token into a cookie
        response = make_response(redirect(url_for('index')))
        response.set_cookie("session_token", session_token, httponly=True, samesite='Strict')

        return response


@app.route("/result", methods=["POST"])
def result():
    guess = int(request.form.get("guess"))

    session_token = request.cookies.get("session_token")

    # get user from the database based on her/his session token
    user = db.query(User).filter_by(session_token=session_token).first()

    if guess == user.secret_num:
        message = f"Congratulations {guess} was the secret number!"
        response = make_response(render_template("win.html", message=message))

        new_secret = random.randint(1, 30)  # create a new random secret number
        user.secret_number = new_secret
        user.save()
        return response
    elif guess < user.secret_num:
        message = f"try a number that's bigger than {guess}"
        return render_template("result.html", message=message)
    elif guess > user.secret_num:
        message = f"try a number that's smaller than {guess}"
        return render_template("result.html", message=message)


if __name__ == '__main__':
    app.run(use_reloader=True)
