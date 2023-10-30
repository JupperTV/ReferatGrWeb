#!/usr/bin/python

# ! NACHHER LÖSCHEN
from os import system
system("cls")
del system

import time
from typing import Final

import flask  # Das Framework

import accountmanager
import entrymanager
import eventmanager
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

@app.route("/dashboard", methods=["GET"])
def dashboard():
    token: str | None = flask.request.cookies.get(COOKIE_NAME_LOGIN_TOKEN)
    print(token)
    email: str | None = accountmanager.GetAccountFromToken(token).email
    return flask.render_template("dashboard.html", email=email)

def gethomebuttontext() -> str:
        if flask.request.cookies.get(COOKIE_NAME_LOGIN_TOKEN):
            return "Zurück zum Dashboard"
        else:
            return "Zurück zur Startseite"

@app.route("/register", methods=["GET", "POST"])
def register():
    if flask.request.method == "GET":
        return flask.render_template("register.html")
    form: dict = flask.request.form
    message = None
    if not accountmanager.EmailIsValid(form["email"]):
        message = "Die E-Mail ist ungültig"
    if accountmanager.UserExists(form["email"]):
        message = "Es gibt schon einen Account, der mit dieser E-Mail registriert ist" if not message else message
    if form["password"] != form["repeatpassword"]:
        message = "Die Passwörter stimmen nicht über ein" if not message else message
    if not accountmanager.PasswordIsValid(form["password"]):
        message = "Das Passwort ist ungültig" if not message else message
    if message:  # Einer der if-Statements war True
        title = "Registrierung"
        # checkIfUserIsLoggedIn() überprüft selber, ob "/" zu /index
        # oder zu /dashboard umleiten soll
        link = flask.url_for("root")
        buttontext = gethomebuttontext()
        return flask.render_template("messageonebutton.html", title=title,
                                     message=message, link=link,
                                     buttontext=buttontext)

    try:
        accountmanager.SaveInCSV(form["email"], form["password"],
                                 form["firstname"], form["lastname"])
    except errors.AccountAlreadyExistsError:
        homebuttontext = gethomebuttontext()
        backbuttontext = "Zurück zur Registrierung"
        message = "Ein Account mit dieser E-Mail ist bereits registriert"
        link = f"{flask.url_for("register")}"
        title="Fehler"
        return flask.render_template("messagetwobuttons.html", title=title,
                                     message=message, backlink=link,
                                     homebuttontext=homebuttontext,
                                     backbuttontext=backbuttontext)

    # msg = f"<h1>You are now registered and logged in with the email {form["email"]}</h1>"
    title = "Registrierung"
    message=f"Die Registrierung war erfolgreich und du bist jetzt  mit der E-Mail {form["email"]} angemeldet"
    link = flask.url_for("dashboard")
    buttontext = "Zum Dashboard"
    response: flask.Response = flask.make_response(
        flask.render_template("messageonebutton.html", title=title, message=message,
                              link=link, buttontext=buttontext)
    )
    response.set_cookie(key=COOKIE_NAME_LOGIN_TOKEN,
                        value=accountmanager.GetAccountFromEmail(
                            form["email"]).accountid
                       )
    return response

@app.route("/login", methods=["GET", "POST"])
def login():
    if flask.request.method == "GET":
        return flask.render_template("login.html")

    form = flask.request.form
    message = None
    if not accountmanager.UserExists(form["email"]):
        message = "Diese E-Mail ist nicht registriert"
    if not accountmanager.PasswordIsValid(form["password"]):
        message = "Das Passwort ist ungültig" if not message else message
    if not accountmanager.LoginIsValid(form["email"], form["password"]):
        message = "Falsches Passwort für Account" if not message else message
    if message:
        title="Fehler"
        backlink = f"{flask.url_for("login")}"
        backbuttontext = "Zurück zum Login"
        homebuttontext = gethomebuttontext()
        return flask.render_template("messagetwobuttons.html", title=title,
                                     message=message, backlink=backlink,
                                     homebuttontext=homebuttontext,
                                     backbuttontext=backbuttontext)

    title="Login"
    # Diese message Variable und die message Variable von davor, haben
    # nichts miteinander zu tun. Ich benenne sie immer noch nicht um,
    # damit alle Variablen, auch wenn sie in anderen Funktionen sind,
    # für {{ message }} in messageonebutton.html oder
    # messageonebutton.html den gleichen Namen haben.
    # Das hilft (für mich) für die Lesbarkeit
    message = f"Du bist jetzt mit der E-Mail {form["email"]} eingeloggt"
    link = flask.url_for("dashboard")
    buttontext = "Zum Dashboard"
    response: flask.Response = flask.make_response(
        flask.render_template("messageonebutton.html", title=title, link=link,
                              message=message, buttontext=buttontext))
    response.set_cookie(key=COOKIE_NAME_LOGIN_TOKEN,
                        value=accountmanager.GetAccountFromEmail(
                            form["email"]).accountid)
    return response

# Entferne den Cookie vom Browser, damit keine Auth. mehr gemacht wird
# Und nicht mehr geprüft wird, welcher Benutzer sich eingeloggt hat
@app.route("/logout", methods=["GET"])
def logout():
    email = accountmanager.GetAccountFromToken(COOKIE_NAME_LOGIN_TOKEN)
    title = "Logout"
    message = f"Der Account mit der E-Mail {email} wurde erfolgreich ausgeloggt"
    link = flask.url_for("index")
    buttontext = "Zurück zur Startseite"
    resp = flask.Response(
        flask.render_template("messageonebutton.html", title=title, link=link,
                              message=message, buttontext=buttontext))
    resp.delete_cookie(COOKIE_NAME_LOGIN_TOKEN)
    return resp

# ALLE Events die erstellt wurden. Auch die, von anderen Benutzern
@app.route("/events", methods=["GET", "POST"])
def events():
    if flask.request.method == "GET":
        loggedin: bool = flask.request.cookies.get(COOKIE_NAME_LOGIN_TOKEN) is not None
        events: list[eventmanager.Event] = eventmanager.GetAllEvents()
        if not events:
            title = "Events"
            message = "Es wurden noch keine Events erstellt"
            link = flask.url_for("root")
            buttontext = gethomebuttontext()
            return flask.render_template("messageonebutton.html", title=title,
                                         message=message, link=link,
                                         buttontext=buttontext)

        for event in events:
            event.epoch = eventmanager.EpochToNormalTime(event.epoch)
            event.eventtype = eventmanager.GetReadableEventType(event.eventtype)
        def getorganizer(event: eventmanager.Event) -> str:
            account = accountmanager.GetAccountFromEmail(event.organizeremail)
            event.description = event.description.replace(";;;", ",")
            return f"{account.firstname} {account.lastname}"
        # isredirect is set on /createentry if entrymanager.DidAccountAlreadyEnter()
        isredirect = flask.request.args.get("isredirect")
        return flask.render_template("events.html", events=events,
                                     list=list, loggedin=loggedin,
                                     getorganizer=getorganizer,
                                     enumerate=enumerate,
                                     eventmanager=eventmanager,
                                     isredirect=isredirect)

    accountid = flask.request.cookies[COOKIE_NAME_LOGIN_TOKEN]

    # Das alles wird ausgeführt, wenn die request methode POST ist.
    # Das einzige, dass im Form übergeben wird, ist der button,
    # der die eventid in seinem Namen hat
    eventid = list(flask.request.form.keys())[0]
    if entrymanager.DidAccountAlreadyEnter(accountid, eventid):
        return flask.redirect(flask.url_for("events", isredirect=True))

    entrymanager.SaveInCSV(accountid, eventid)

    title = "Events"
    message = f"Du hast dich zum event '{eventmanager.GetEventFromId(eventid).eventname}' erfolgreich eingetragen"
    backlink = flask.url_for("events")
    backbuttontext = "Zurück zu allen Events"
    homebuttontext = gethomebuttontext()
    return flask.render_template("messagetwobuttons.html", title=title,
                                 message=message, backlink=backlink,
                                 backbuttontext=backbuttontext,
                                 homebuttontext=homebuttontext)

# This just gathers all of necessary data e.g. email and eventname and
# returns it as a dict

def FinishCreateEvent(cookies: dict, form: dict[str, str]) -> dict[str, str]:
    # * Notiz: Das datetime-local input ist im ISO 860-Format.
    # * Trotzdem gibt das datetime objekt keine Zeitzone zurück.
    # * D.h. Das Datum wird als "yyyy-mm-ddThh:mm" gespeichert.
    # (Anscheinend ist das T zur Trennung da)
    organizertoken = cookies[COOKIE_NAME_LOGIN_TOKEN]
    organizeremail = accountmanager.GetAccountFromToken(organizertoken).email

    f = lambda s: form[s]
    eventname = f(eventmanager.CSVHeader.NAME)
    epoch: float = eventmanager.InputTimeToEpoch(f("datetime"))
    description = f(eventmanager.CSVHeader.DESCRIPTION).replace(",", ";;;")
    eventtype = f(eventmanager.CSVHeader.EVENTTYPE)

    # Daten zu einem Ort sind abhängig von eventmanager.EventType
    # bzw. eventmanager.Event.eventtype
    country = ""
    city = ""
    zipcode: str = ""
    street = ""
    housenumber: str = ""
    if eventtype == eventmanager.EventType.ON_SITE:
        country = f(eventmanager.CSVHeader.COUNTRY)
        city = f(eventmanager.CSVHeader.CITY)
        zipcode: str = f(eventmanager.CSVHeader.ZIPCODE)
        street = f(eventmanager.CSVHeader.STREET)
        housenumber: str = f(eventmanager.CSVHeader.HOUSENUMBER)

    # Etwas bessere Lesbarkeit
    h = eventmanager.CSVHeader
    # Der einzige Header, der hier nichtzurückgegeben wird, ist die ID, die in
    # eventmanager erstellt wird
    return { h.NAME: eventname, h.EPOCH: epoch, h.EVENTTYPE: eventtype,
             h.ORGANIZER_EMAIL: organizeremail, h.COUNTRY: country, h.CITY: city,
             h.ZIPCODE: zipcode, h.STREET: street, h.HOUSENUMBER: housenumber,
             h.DESCRIPTION: description }

# Ein neues Event erstellen
@app.route("/createevent", methods=["GET", "POST"])
def createevent():
    if flask.request.method == "GET":
        return flask.render_template("createevent.html",
                                     EventType=eventmanager.EventType,
                                     formlink=flask.url_for("createevent"),
                                     ismodify=False,
                                     eventtype = eventmanager.EventType.ON_SITE)
    form: dict[str, str] = dict(flask.request.form)
    eventdata: dict = FinishCreateEvent(flask.request.cookies, form)
    try:
        pass
        eventmanager.CreateEventFromForm(*eventdata.values())
    except errors.EventAlreadyExistsError:
        title = "Fehler"
        message = "Das Event existiert bereits"
        backlink = flask.url_for("createevent")
        backbuttontext = "Zurück zur Eventerstellung"
        homebuttontext = gethomebuttontext()
        return flask.render_template("messagetwobuttons.html", title=title,
                                     message=message, backlink=backlink,
                                     backbuttontext=backbuttontext,
                                     homebuttontext=homebuttontext)

    eventname = form.get(eventmanager.CSVHeader.NAME)
    token = flask.request.cookies.get(COOKIE_NAME_LOGIN_TOKEN)
    organizeremail = accountmanager.GetAccountFromToken(token).email
    title="Eventerstellung"
    message = f"Das Event '{eventname}' wurde von dir mit der Email {organizeremail} erstellt"
    backlink = flask.url_for("events")
    backbuttontext = "Zu den Events"
    homebuttontext = gethomebuttontext()
    return flask.render_template("messagetwobuttons.html", title=title,
                                 message=message, backlink=backlink,
                                 backbuttontext=backbuttontext,
                                 homebuttontext=homebuttontext)

# Alle Einträge, die der Account gemacht hat
@app.route("/entries", methods=["GET", "POST"])
def entries():
    if flask.request.method == "GET":
        accountid = flask.request.cookies[COOKIE_NAME_LOGIN_TOKEN]
        events: list[eventmanager.Event] = entrymanager.GetAllEntriedEventsOfAccount(accountid)

        if not events:
            title = "Fehler"
            message = "Du hast noch zu keinem Event eingetragen"
            backlink = flask.url_for("events")
            backbuttontext = "Zu den Events"
            homebuttontext = gethomebuttontext()
            return flask.render_template("messagetwobuttons.html", title=title,
                                         message=message, backlink=backlink,
                                         backbuttontext=backbuttontext,
                                         homebuttontext=homebuttontext)

        loggedin = flask.request.cookies.get(COOKIE_NAME_LOGIN_TOKEN) is not None

        for event in events:
            event.eventtype = eventmanager.GetReadableEventType(event.eventtype)
            event.epoch = eventmanager.EpochToNormalTime(event.epoch)

        def getorganizer(event: eventmanager.Event) -> str:
            account = accountmanager.GetAccountFromEmail(event.organizeremail)
            event.description = event.description.replace(";;;", ",")
            return f"{account.firstname} {account.lastname}"

        return flask.render_template(
                "entries.html", events=events, enumerate=enumerate,
                loggedin=loggedin, eventmanager=eventmanager, list=list,
                getorganizer=getorganizer)

    # Ab hier ist der code für POST Requests
    eventid = list(flask.request.form.keys())[0]
    accountid = flask.request.cookies[COOKIE_NAME_LOGIN_TOKEN]
    entrymanager.DeleteEntry(accountid, eventid)

    title = "Einträge"
    message = f"Dein Eintrag zum Event '{eventmanager.GetEventFromId(eventid).eventname}' wurde erfolgreich gelöscht"
    backlink = flask.url_for("entries")
    backbuttontext = "Zurück zu den Einträgen"
    homebuttontext = gethomebuttontext()
    return flask.render_template("messagetwobuttons.html", title=title,
                                 message=message, backlink=backlink,
                                 backbuttontext=backbuttontext,
                                 homebuttontext=homebuttontext)

# Alle Events, die der Nutzer erstellt hat
@app.route("/myevents", methods=["GET", "POST"])
def myevents():
    if flask.request.method == "GET":
        token = flask.request.cookies[COOKIE_NAME_LOGIN_TOKEN]
        email = accountmanager.GetAccountFromToken(token).email
        title = "Meine Events"
        try:
            createdevents = eventmanager.GetAllEventsCreatedByOrganizer(email)
        except errors.AccountHasNoEventsError:
            message = "Du hast noch keine Events erstellt"
            backlink = flask.url_for("createevent")
            backbuttontext = "Ein Event erstellen"
            homebuttontext = gethomebuttontext()
            return flask.render_template("messagetwobuttons.html", title=title,
                                         message=message, backlink=backlink,
                                         backbuttontext=backbuttontext,
                                         homebuttontext=homebuttontext)
        for event in createdevents:
            event.epoch = eventmanager.EpochToNormalTime(event.epoch)
            event.eventtype = eventmanager.GetReadableEventType(event.eventtype)
        return flask.render_template("myevents.html", list=list,
                                     events=createdevents, enumerate=enumerate,
                                     eventmanager=eventmanager)

    # Ein POST Request wird gesendet, wenn ein Event gelöscht wird
    eventid = list(flask.request.form.keys())[0]
    eventmanager.DeleteEvent(eventid)
    title = "Meine Events"
    message = "Das Event wurde erfolgreich gelöscht."
    backlink = flask.url_for("myevents")
    backbuttontext = "Zurück zu deinen Events"
    homebuttontext = gethomebuttontext()
    return flask.render_template("messagetwobuttons.html", title=title,
                                 message=message, backlink=backlink,
                                 backbuttontext=backbuttontext,
                                 homebuttontext=homebuttontext)

@app.route("/modifyevent", methods=["GET", "POST"])
def modifyevent():
    # Notiz: Die ID des Events ist der erste und einzige Schlüssel in den
    # args. des GET Requests
    # Die Eventdaten werden als Form übergeben
    if flask.request.method == "GET":
        print("Args:", dict(flask.request.args))
        print("Form:", dict(flask.request.form))
        eventid = list(flask.request.args.keys())[0]
        originalevent = eventmanager.GetEventFromId(eventid)
        # Damit ich weniger schreiben muss
        headers = eventmanager.CSVHeader
        eventdict = dict(zip(headers.AsList(), list(originalevent)))
        isonline = eventdict.get(headers.EVENTTYPE) == eventmanager.EventType.ONLINE
        eventdict[headers.EPOCH] = eventmanager.EpochToInputTime(eventdict[headers.EPOCH])
        # createevent wird wiederverwendet, weil die Inputs gleich sind.
        return flask.render_template("createevent.html",
                                     ismodify=True, eventid=eventid,
                                     EventType=eventmanager.EventType,
                                     formlink=flask.url_for("modifyevent"),
                                     isonline = isonline, **eventdict)

    # eventdata: dict = FinishCreateEvent(form)
    # eventid = flask.request.args.keys()
    # eventdata.update({eventmanager.CSVHeader.EVENTID: eventid})
    # event = eventmanager.Event.InitFromDict(eventdata)
    # eventmanager.ModifyEvent(event)
    print("Args:", dict(flask.request.args))
    print("Form:", dict(flask.request.form))
    return "Ende"


@app.before_request
def checkIfUserIsLoggedIn():
    token: str | None = flask.request.cookies.get(COOKIE_NAME_LOGIN_TOKEN)
    allowedSitesIfNotLoggedIn: list[str] = ["index","register","login","events"]
    # Durch dieses if-Statement habe ich, ohne es zu bemerken,
    # verhindert, dass Seiten, die garnicht existieren, wie z.B. /abcde,
    # den error code 404 ausgeben
    if (not token) and (flask.request.endpoint not in allowedSitesIfNotLoggedIn):
        return flask.redirect(flask.url_for("index"))
    if token and flask.request.endpoint == "index":
        return flask.redirect(flask.url_for("dashboard"))
    # Nicht wird ausgegeben


if __name__ == "__main__":
    DEFAULT_HTTP_PORT = 80  # Zur Vermeidung von Magic Numbers
    app.run(port=DEFAULT_HTTP_PORT, debug=True)

