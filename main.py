import random
import os

from flask import Flask, render_template, request, make_response, redirect, url_for
from sqla_wrapper import SQLAlchemy

app = Flask(__name__)
db_url = os.getenv("DATABASE_URL", "sqlite:///db.sqlite").replace("postgres://", "postgresql://", 1)
db = SQLAlchemy(db_url)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    secret_num = db.Column(db.Integer, unique=False)


db.create_all()


@app.route("/", methods=["GET"])
def index():
    email_address = request.cookies.get("email")  # check if there is a cookie with user
    if email_address:  # get user from the database based on email address
        user = db.query(User).filter_by(email=email_address).first()
    else:
        user = None

    return render_template("index.html", user=user)


@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("user-name")
    email = request.form.get("user-email")
    secret_num = int(random.randint(1, 30))

    # see if user already exists
    user = db.query(User).filter_by(email=email).first()

    # create a User object
    if not user:
        user = User(name=name, email=email, secret_num=secret_num)
        user.save()  # save user into the database

    # save user's email into a cookie
    response = make_response(redirect(url_for('index')))
    response.set_cookie("email", email)
    response.set_cookie("name", name)

    return response


@app.route("/result", methods=["POST"])
def result():
    guess = int(request.form.get("guess"))

    email_address = request.cookies.get("email")

    # get user from the database based on her/his email address
    user = db.query(User).filter_by(email=email_address).first()

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

    @app.route("/logout", methods=["GET"])
    def logout():
        response = make_response(redirect(url_for('index')))
        response.set_cookie("email", expires=0)
        response.set_cookie("name", expires=0)

        return response


if __name__ == '__main__':
    app.run(use_reloader=True)
