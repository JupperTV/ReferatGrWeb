#!/usr/bin/python

# ! NACHHER LÖSCHEN
from os import system
system("cls")
del system

import time
from typing import Final

import flask  # Das Framework

import entrymanager
import eventmanager
import accountmanager
import errors

# I don't know what static_folder is for but I use it anyway just in case
app = flask.Flask(__name__, static_folder="static", template_folder="static")

COOKIE_NAME_LOGIN_TOKEN: Final[str] = "FranzWebProj"

@app.route("/", methods=["GET"])
def root():
    return flask.redirect(flask.url_for("index"))

@app.route("/index", methods=["GET"])
def index():
    return flask.render_template("index.html")

# TODO
@app.route("/dashboard", methods=["GET"])
def dashboard():
    token: str | None = flask.request.cookies.get(COOKIE_NAME_LOGIN_TOKEN)
    email: str | None = accountmanager.GetEmailFromToken(token)
    return f"Dashboard von {email}"

# DONE
@app.route("/register", methods=["GET", "POST"])
def register():
    if flask.request.method == "GET":
        return flask.render_template("register.html")
    form: dict = flask.request.form
    if accountmanager.UserExists(form["email"]):
        return "There is already an account registered with that email"
    if form["password"] != form["repeatpassword"]:
        return "The passwords are not the same"
    try:
        accountmanager.AddRegistration(form["email"], form["password"],
                                       form["firstname"], form["lastname"])
    except errors.AccountAlreadyExistsError:
        return "There is already an account registered with that email"
    msg = f"You are now registered and logged in with the email {form["email"]}"
    response: flask.Response = flask.make_response(msg)
    response.set_cookie(key=COOKIE_NAME_LOGIN_TOKEN,
                        value=accountmanager.GetUserToken(form["email"]))
    return response

# POST: Überprüfe Login Daten.
# TODO? Wenn es erfolgreich ist, gehe in Zukunft vielleicht zum Dashboard
@app.route("/login", methods=["GET", "POST"])
def login():
    if flask.request.method == "GET":
        return flask.render_template("login.html")

    form = flask.request.form
    if not accountmanager.UserExists(form["email"]):
        return "There is no account with this email"
    if not accountmanager.PasswordIsValid(form["password"]):
        return "Invalid password"
    if not accountmanager.LoginIsValid(form["email"], form["password"]):
        return "Wrong password"

    msg = f"You are now logged in with the email {form["email"]}"
    response: flask.Response = flask.make_response(msg)
    response.set_cookie(key=COOKIE_NAME_LOGIN_TOKEN,
                        value=accountmanager.GetUserToken(form["email"]))
    return response

# Entferne den Cookie vom Browser, damit keine Auth. mehr gemacht wird
# Und nicht mehr geprüft wird, welcher Benutzer sich eingeloggt hat
@app.route("/logout", methods=["GET"])
def logout():
    resp = flask.Response("Succesfully logged out")
    resp.delete_cookie(COOKIE_NAME_LOGIN_TOKEN)
    return resp

#region Delete?
# # DONE
# @app.route("/finishregister", methods=["GET", "POST"])
# def finishregister():
#     form: dict = flask.request.form
#     if accountmanager.UserExists(form["email"]):
#         return "There is already an account registered with that email"
#     if form["password"] != form["repeatpassword"]:
#         return "The passwords are not the same"
#     try:
#         accountmanager.AddRegistration(form["email"], form["password"],
#                                        form["firstname"], form["lastname"])
#     except errors.AccountAlreadyExistsError:
#         return "There is already an account registered with that email"
#     msg = f"You are now registered and logged in with the email {form["email"]}"
#     response: flask.Response = flask.make_response(msg)
#     response.set_cookie(key=COOKIE_NAME_LOGIN_TOKEN,
#                         value=accountmanager.GetUserToken(form["email"]))
#     return response

# @app.route("/checklogin", methods=["GET", "POST"])
# def checklogin():
#     if flask.request.method != "POST":
#         return flask.redirect(flask.url_for("login"))
#
#     form = flask.request.form
#     if not accountmanager.UserExists(form["email"]):
#         return "There is no account with this email"
#     if not accountmanager.PasswordIsValid(form["password"]):
#         return "Invalid password"
#     if not accountmanager.LoginIsValid(form["email"], form["password"]):
#         return "Wrong password"
#
#     msg = f"You are now logged in with the email {form["email"]}"
#     response: flask.Response = flask.make_response(msg)
#     response.set_cookie(key=COOKIE_NAME_LOGIN_TOKEN,
#                         value=accountmanager.GetUserToken(form["email"]))
#     return response
#endregion

# ALLE Events die erstellt wurde, auch die, von anderen Benutzern
@app.route("/allevents", methods=["GET", "POST"])
def allevents():
    if flask.request.method == "GET":
        allEvents: list[eventmanager.Events] = eventmanager.GetAllEvents()
        if not allEvents:
            return "No Events :("
        scriptIfRedirect = ""
        # isredirect is set on /createentry if entrymanager.DidAccountAlreadyEnter
        if flask.request.args.get("isredirect"):
            print("TRUE")
            scriptIfRedirect = "<script>alert('You have already entered the event')</script>"
        return flask.render_template("allevents.html", list=list,
                                    eventmanager=eventmanager,
                                     enumerate=enumerate).replace(
                                     "<body>", "<body>"+scriptIfRedirect
                                    )

    # * else flask.request.method is sowieso POST

    # Das einzige, dass im Form übergeben wird, ist der button,
    # ist der Button, der die eventid in seinem Namen hat
    accountid = flask.request.cookies[COOKIE_NAME_LOGIN_TOKEN]
    eventid = list(flask.request.form.keys())[0]
    if entrymanager.DidAccountAlreadyEnter(accountid, eventid):
        return flask.redirect(flask.url_for("allevents", isredirect=True))
    entrymanager.CreateEntry(accountid, eventid)
    return ":)"

# # Account trägt sich in das Event mit der id ```eventid``` ein
# @app.route("/createentry", methods=["POST"])
# def createentry():
#     # Das einzige, dass im Form übergeben wird, ist der button,
#     # ist der Button, der die eventid in seinem Namen hat
#     accountid = flask.request.cookies[COOKIE_NAME_LOGIN_TOKEN]
#     eventid = list(flask.request.form.keys())[0]
#     if entrymanager.DidAccountAlreadyEnter(accountid, eventid):
#         return flask.redirect(flask.url_for("allevents", isredirect=True))
#     entrymanager.CreateEntry(accountid, eventid)
#     return ":)"

# Ein neues Event erstellen
@app.route("/createevent", methods=["GET", "POST"])
def createevent():
    if flask.request.method == "GET":
        return flask.render_template("createevent.html")
    form: dict[str, str] = flask.request.form
    # * Notiz: Das datetime-local input ist im ISO 860-Format.
    # * Trotzdem gibt das datetime objekt keine Zeitzone zurück.
    # * D.h. Das Datum wird als "yyyy-mm-ddThh:mm" gespeichert.
    # (Anscheinend ist das T zur Trennung da)
    f = lambda s: form[s]
    # region getitems from form
    datetime: time.struct_time = time.strptime(f("datetime"), "%Y-%m-%dT%H:%M")
    eventname = f("eventname")
    epoch: float = float(time.mktime(datetime))
    country = f("country")
    city = f("city")
    zipcode: str = f("zipcode")
    street = f("street")
    housenumber: str = f("housenumber")
    organizertoken = flask.request.cookies[COOKIE_NAME_LOGIN_TOKEN]
    organizeremail = accountmanager.GetEmailFromToken(organizertoken)
    description = f("description")
    # endregion

    eventmanager.CreateEventFromForm(
            eventname=eventname, epoch=epoch, organizeremail=organizeremail,
            country=country, city=city, zipcode=zipcode, street=street,
            housenumber=housenumber, description=description
    )
    return f"Das Event '{eventname}' wurde von dir mit der Email {organizeremail} erstellt"

# Alle Einträge, die der Account gemacht hat
@app.route("/entries", methods=["GET", "POST"])
def entries():
    if flask.request.method == "GET":
        accountid = flask.request.cookies[COOKIE_NAME_LOGIN_TOKEN]
        events: list[eventmanager.Event] = entrymanager.GetAllEntriedEventsOfAccount(accountid)
        if not events:
            return "This account doesn't have any entries"
        return flask.render_template(
                "entriedevents.html", events=events, enumerate=enumerate,
                eventmanager=eventmanager, list=list)

    # else flask.request.method == "POST"

    eventid = list(flask.request.form.keys())[0]
    accountid = flask.request.cookies[COOKIE_NAME_LOGIN_TOKEN]
    try:
        entrymanager.DeleteEntry(accountid, eventid)
    except erros.AccountHasNoEntriesError:
        return "This account does not have any entries"
    return ":)"

# Alle Events, die der Nutzer erstellt hat
@app.route("/myevents", methods=["GET", "POST"])
def myevents():
    if flask.request.method == "GET":
        accountid = flask.request.cookies[COOKIE_NAME_LOGIN_TOKEN]
        email = accountmanager.GetEmailFromToken(accountid)
        createdevents = eventmanager.GetAllEventsCreatedByOrganizer(email)
        return flask.render_template("createdevents.html", list=list,
                                     events=createdevents, enumerate=enumerate,
                                     eventmanager=eventmanager)

    # * else flask.request.method == "POST"
    eventid = list(flask.request.form.keys())[0]
    try:
        eventmanager.DeleteEvent(eventid)
    except errors.AccountHasNoEntriesError:
        return "This account does not have any entries"
    return ":)"

# @app.route("/deleteentry", methods=["POST"])
# def deleteentry():
#     eventid = list(flask.request.form.keys())[0]
#     accountid = flask.request.cookies[COOKIE_NAME_LOGIN_TOKEN]
#     try:
#         entrymanager.DeleteEntry(accountid, eventid)
#     except erros.AccountHasNoEntriesError:
#         return "This account does not have any entries"
#     return ":)"

# @app.route("/deleteevent", methods=["POST"])
# def deleteevent():
#     eventid = list(flask.request.form.keys())[0]
#     try:
#         eventmanager.DeleteEvent(eventid)
#     except errors.AccountHasNoEntriesError:
#         return "This account does not have any entries"
#     return ":)"

@app.before_request
def checkIfUserIsLoggedIn():
    token: str | None = flask.request.cookies.get(COOKIE_NAME_LOGIN_TOKEN)
    allowedSitesIfNotLoggedIn: list[str] = ["index", "register", "login",
                                            "checklogin", "finishregister"]
    if (not token) and (flask.request.endpoint not in allowedSitesIfNotLoggedIn):
        return flask.redirect(flask.url_for("index"))
    if token and flask.request.endpoint == "index":
        return flask.redirect(flask.url_for("dashboard"))
    # return nothing and continue to the requested site


if __name__ == "__main__":
    DEFAULT_HTTP_PORT = 80  # Zur Vermeidung von Magic Numbers
    app.run(port=DEFAULT_HTTP_PORT, debug=True)

