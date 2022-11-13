import random

from flask import Flask, render_template, request, make_response


app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    secret_num = request.cookies.get("secret_num")  # check if there is a cookie

    response = make_response(render_template("index.html"))
    if not secret_num:  # if there is no cookie, create a new one
        new_secret_num = random.randint(1, 30)
        response.set_cookie("secret_num", str(new_secret_num))

    return response


@app.route("/result", methods=["POST"])
def result():
    secret_num = int(request.cookies.get("secret_num"))
    guess = int(request.form.get("guess"))

    if guess == secret_num:
        message = f"Congratulations {guess} was the secret number!"
        response = make_response(render_template("win.html", message=message))
        response.set_cookie("secret_num", expires=0)
        return response
    elif guess < secret_num:
        message = f"try a number that's bigger than {guess}"
        return render_template("result.html", message=message)
    elif guess > secret_num:
        message = f"try a number that's smaller than {guess}"
        return render_template("result.html", message=message)


if __name__ == '__main__':
    app.run(use_reloader=True)
