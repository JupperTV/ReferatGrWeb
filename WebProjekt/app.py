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
    # if not token:  # Benutzer is nicht eingeloggt
    #     return flask.redirect(flask.url_for("index"))
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

@app.route("/logout", methods=["GET"])
def logout():

    resp = flask.Response("Succesfully logged out")
    resp.delete_cookie(COOKIE_NAME_LOGIN_TOKEN)
    return resp

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
        accountmanager.AddRegistration(form["email"], form["password"],
                                       form["firstname"], form["lastname"])
    except errors.AccountAlreadyExistsError:
        return "There is already an account registered with that email"

    msg = f"Your email is now registered and you are logged in as {form["email"]}"
    response: flask.Response = flask.make_response(msg)
    response.set_cookie(key=COOKIE_NAME_LOGIN_TOKEN,
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

    msg = f"You are now logged in as {form["email"]}"
    response: flask.Response = flask.make_response(msg)
    response.set_cookie(key=COOKIE_NAME_LOGIN_TOKEN,
                        value=accountmanager.GetUserToken(form["email"]))
    return response


@app.route("/allevents")
def allevents():
    allEvents: list[eventmanager.Events] = eventmanager.GetAllEvents()
    if not allEvents:
        return "No Events :("
    scriptIfRedirect = ""
    # isredirect is set on /createentry if entrymanager.DidAccountAlreadyEnter
    if flask.request.args.get("isredirect"):
        print("TRUE")
        scriptIfRedirect = "<script>alert('You have already entered the event')</script>"
    return flask.render_template("allevents.html", eventmanager=eventmanager,
                                 enumerate=enumerate, list=list).replace(
                                     "<body>", "<body>"+scriptIfRedirect
                                     )

@app.route("/createentry", methods=["POST"])
def createentry():
    # Das einzige, dass im Form übergeben wird, ist der button,
    # ist der Button, der die eventid in seinem Namen hat
    accountid = flask.request.cookies[COOKIE_NAME_LOGIN_TOKEN]
    eventid = list(flask.request.form.keys())[0]
    if entrymanager.DidAccountAlreadyEnter(accountid, eventid):
        print(True)
        return flask.redirect(flask.url_for("allevents", isredirect=True))
    entrymanager.CreateEntry(accountid, eventid)
    return ":)"

# Done
@app.route("/createevent", methods=["GET", "POST"])
def createevent():
    if flask.request.method == "GET":
        return flask.render_template("createevent.html")
    form: dict[str, str] = flask.request.form
    # * Notiz: Das datetime-local input ist im ISO 860-Format
    # * Trotzdem gibt das datetime objekt keine Zeitzone zurück.
    # * D.h. Das Datum wird als "yyyy-mm-ddThh:mm" gespeichert.
    # (Anscheinend ist das T nur als Trennung da)

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
    # endregion

    eventmanager.CreateEventFromForm(
            eventname=eventname, epoch=epoch, organizeremail=organizeremail,
            country=country, city=city, zipcode=zipcode, street=street,
            housenumber=housenumber
    )
    return f"Das Event '{eventname}' wurde von dir mit der Email {organizeremail} erstellt"

# TODO Events für den zur Zeit angemeldeten Nutzer anzeigen
@app.route("/events")
def events():
    accountid = flask.request.cookies[COOKIE_NAME_LOGIN_TOKEN]
    events: list[eventmanager.Event] = entrymanager.GetAllEntriedEventsOfAccount(accountid)
    return flask.render_template(
            "entriedevents.html", events=events, enumerate=enumerate,
            eventmanager=eventmanager, list=list)

# TODO
@app.route("/deleteentry", methods=["POST"])
def deleteent():
    return ":)"
    raise NotImplementedError()

# TODO
@app.route("/deleteevent", methods=["POST"])
def deleteevent():
    raise NotImplementedError()

@app.before_request
def checkIfUserIsLoggedIn():
    token: str | None = flask.request.cookies.get(COOKIE_NAME_LOGIN_TOKEN)
    allowedSitesIfNotLoggedIn: list[str] = ["index", "register", "login",
                                            "checklogin", "finishregister"]
    if (not token) and (flask.request.endpoint not in allowedSitesIfNotLoggedIn):
        return flask.redirect(flask.url_for("index"))
    # return nothing and continue to the requested site

if __name__ == "__main__":
    DEFAULT_HTTP_PORT = 80  # Zur Vermeidung von Magic Numbers
    app.run(port=DEFAULT_HTTP_PORT, debug=True)

