#!/usr/bin/python

from os import system # ! NOTIZ: NACHHER LÖSCHEN
system("cls")
del system

import time
from typing import Final

import flask  # Das Framework

import entrymanager
import eventmanager
import accountmanager
import errors

app = flask.Flask(__name__, static_folder="static", template_folder="static")

COOKIE_NAME: Final[str] = "FranzWebProj"

# region GET-ers
@app.route("/", methods=["GET"])
def root():
    return flask.redirect(flask.url_for("index"))

@app.route("/index", methods=["GET"])
def index():
    token: str = flask.request.cookies.get(COOKIE_NAME)
    return flask.render_template("index.html")

# TODO
@app.route("/dashboard", methods=["GET"])
def dashboard():
    token: str | None = flask.request.cookies.get(COOKIE_NAME)
    if not token:  # Benutzer is nicht eingeloggt
        return flask.redirect(flask.url_for("index"))
    email: str | None = accountmanager.GetEmailFromToken(token)
    return f"Dashboard von {email}"

# DONE
@app.route("/register", methods=["GET"])
def register():
    return flask.render_template("register.html")

# DONE
@app.route("/login", methods=["GET"])
def login():
    return flask.render_template("login.html")
# endregion

# DONE
@app.route("/finishregister", methods=["GET", "POST"])
def finishregister():
    if flask.request.method != "POST":
        return flask.redirect(flask.url_for("login"))

    form: dict = flask.request.form
    if accountmanager.UserExists(form["email"]):
        return "There is already an account registered with that email"
    if form["password"] != form["repeatpassword"]:
        return "The passwords are not the same"

    try:
        accountmanager.AddRegistration(form["email"], form["password"], form["firstname"], form["lastname"])
    except errors.AccountAlreadyExistsError:
        return "There is already an account registered with that email"

    response: flask.Response = flask.make_response(f"Your email is now registered and you are logged in as {form["email"]}")
    response.set_cookie(key=COOKIE_NAME,
                        value=accountmanager.GetUserToken(form["email"]))
    return response

# DONE
@app.route("/checklogin", methods=["GET", "POST"])
def checklogin():
    if flask.request.method != "POST":
        return flask.redirect(flask.url_for("login"))

    form = flask.request.form
    if not accountmanager.UserExists(form["email"]):
        return "There is no account with this email"
    if not accountmanager.PasswordIsValid(form["password"]):
        return "Invalid password"
    if not accountmanager.LoginIsValid(form["email"], form["password"]):
        return "Wrong password"

    response: flask.Response = flask.make_response(f"You are now logged in as {form["email"]}")
    response.set_cookie(key=COOKIE_NAME,
                        value=accountmanager.GetUserToken(form["email"]))
    return response

# TODO
@app.route("/allevents")
def allevents():
    allEvents: list[eventmanager.Events] = eventmanager.GetAllEvents()
    if not allEvents:
        return "No Events :("
    ret = ""
    keys = ["id","name","epoch","organizer","country","city","zipcode","street","housenumber"]
    for event in allEvents:
        evlist = list(event)
        for index, key in enumerate(keys):
            ret += "&nbsp;" * 4  # 4 Leerzeichen anstatt ein Tab
            ret += f"{key}: {evlist[index]}<br>"
        ret += "<br><br>"
    return ret

# TODO. Der Unterschied zwischen /allevents und /events, ist dass /events die
# Events für den zur Zeit angemeldeten Nutzer anzegit, anstatt ALLE Events
@app.route("/events")
def events():
    raise NotImplementedError()

# TODO!!! Daten aus Form in einen eventmanager.Event packen und dann speichern
@app.route("/createevent", methods=["GET", "POST"])
def createevent():
    if flask.request.method == "GET":
        return flask.render_template("createevent.html")
    form: dict[str, str] = flask.request.form
    # * Notiz: Das datetime-local input wird in ISO 8601 ohne Zeitzonen übergeben.
    # * D.h. Das Datum wird als "yyyy-mm-ddThh:mm" gespeichert.
    # * Anscheinend ist das T nur als Trennung da

    datetime: time.struct_time = time.strptime(form["date"], "%Y-%m-%dT%H:%M")
    epoch: float = float(time.mktime(datetime))
    return ":)"

# TODO
@app.route("/deleteevent")
def deleteevent():
    raise NotImplementedError()

if __name__ == "__main__":
    DEFAULT_HTTP_PORT = 80  # Zur Vermeidung von Magic Numbers
    app.run(port=DEFAULT_HTTP_PORT, debug=True)

