#!/usr/bin/python

from os import system # ! NOTIZ: NACHHER LÖSCHEN
system("cls")
del system

import flask  # Das Hauptframework, das hier benutzt wird

import entrymanager
import eventmanager
import accountmanager
import errors

app = flask.Flask(__name__, static_folder="static", template_folder="static")

@app.route("/", methods=["GET"])
def home():
    return flask.redirect(flask.url_for("index"))

@app.route("/index", methods=["GET"])
def index():
    return flask.render_template("index.html")

# TODO
@app.route("/login", methods=["GET"])
def login():
    return flask.render_template("login.html")

# TODO
@app.route("/checklogin", methods=["GET", "POST"])
def checklogin():
    if flask.request.method != "POST":
        return flask.redirect(flask.url_for("login"))
    return ""


# DONE
@app.route("/register", methods=["GET"])
def register():
    return flask.render_template("register.html")

# DONE
@app.route("/finishregister", methods=["GET", "POST"])
def finishregister():
    if flask.request.method != "POST":
        return flask.redirect(flask.url_for("login"))

    form: dict = flask.request.form
    if accountmanager.UserExists(form["email"]):
        return "There is already an account registered with that email"
    if form["password"] != form["repeatpassword"]:
        pass  # Do something
        return "password is not the same"
    
    try:
        accountmanager.AddRegistration(form["email"], form["password"], form["firstname"], form["lastname"])
    except errors.AccountAlreadyExists:
        return "There is already an account registered with that email"
    return f"formstuff:<br>{"<br>".join([f"{k}: {v}" for k, v in form.items()])}<br><br>"

# TODO
@app.route("/events")
def events():
    raise NotImplementedError()

# TODO
@app.route("/createevent")
def createevent():
    raise NotImplementedError()

# TODO
@app.route("/deleteevent")
def deleteevent():
    raise NotImplementedError()

if __name__ == "__main__":
    DEFAULT_HTTP_PORT = 80  # Zur Vermeidung von Magic Numbers
    app.run(port=DEFAULT_HTTP_PORT, debug=True)
