#!/usr/bin/python

import time
from typing import Final

import flask  # The framework

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
    email: str | None = accountmanager.GetAccountFromToken(token).email
    return flask.render_template("dashboard.html", email=email)

def gethomebuttontext() -> str:
    if flask.request.cookies.get(COOKIE_NAME_LOGIN_TOKEN):
        return "Back to dashboard"
    else:
        return "Back to home page"

@app.route("/register", methods=["GET", "POST"])
def register():
    if flask.request.method == "GET":
        homebuttontext = gethomebuttontext()
        return flask.render_template("register.html",
                                    homebuttontext=homebuttontext)
    form: dict = flask.request.form
    message = None
    if not accountmanager.EmailIsValid(form["email"]):
        message = "Invalid e-mail"
    if accountmanager.UserExists(form["email"]):
        message = "An account with this e-mail already exists" if not message else message
    if form["password"] != form["repeatpassword"]:
        message = "The passwords do not match" if not message else message
    if not accountmanager.PasswordIsValid(form["password"]):
        message = "Invalid password" if not message else message
    if message:  # This is true if a previous if statements was true
        title = "Register"
        # checkIfUserIsLoggedIn() checks if "/" should redirect to
        # /index or /dashboard
        link = flask.url_for("root")
        homebuttontext = gethomebuttontext()
        return flask.render_template("messageonebutton.html", title=title,
                                     message=message, link=link,
                                     homebuttontext=homebuttontext)

    try:
        accountmanager.SaveInCSV(form["email"], form["password"],
                                 form["firstname"], form["lastname"])
    except errors.AccountAlreadyExistsError:
        homebuttontext = gethomebuttontext()
        backbuttontext = "Back to registration"
        message = "An account with this e-mail already exists"
        link = f"{flask.url_for("register")}"
        title="Fehler"
        return flask.render_template("messagetwobuttons.html", title=title,
                                     message=message, backlink=link,
                                     homebuttontext=homebuttontext,
                                     backbuttontext=backbuttontext)

    # msg = f"<h1>You are now registered and logged in with the email {form["email"]}</h1>"
    title = "Register"
    message=f"The registration was succesful. Logged in with e-mail {form["email"]}"
    link = flask.url_for("dashboard")
    homebuttontext = "To dashboard"
    response: flask.Response = flask.make_response(
        flask.render_template("messageonebutton.html", title=title, message=message,
                              link=link, homebuttontext=homebuttontext)
    )
    response.set_cookie(key=COOKIE_NAME_LOGIN_TOKEN,
                        value=accountmanager.GetAccountFromEmail(
                            form["email"]).accountid
                       )
    return response

@app.route("/login", methods=["GET", "POST"])
def login():
    if flask.request.method == "GET":
        homebuttontext = gethomebuttontext()
        return flask.render_template("login.html", homebuttontext=homebuttontext)

    form = flask.request.form
    message = None
    if not accountmanager.UserExists(form["email"]):
        message = "This e-mail is not registered"
    if not accountmanager.PasswordIsValid(form["password"]):
        message = "Invalid password" if not message else message
    if not accountmanager.LoginIsValid(form["email"], form["password"]):
        message = "Wrong password" if not message else message
    if message:
        title="Error"
        backlink = f"{flask.url_for("login")}"
        backbuttontext = "Back to Login"
        homebuttontext = gethomebuttontext()
        return flask.render_template("messagetwobuttons.html", title=title,
                                     message=message, backlink=backlink,
                                     homebuttontext=homebuttontext,
                                     backbuttontext=backbuttontext)

    title="Log in"
    # This message variable and the one before are not related. They
    # still have the same name so that all the message variables,
    # even if they are in different functions, share the same name.
    # This just increases readability and consistency, because in
    # messageonebutton.html and messageonebutton.html, the placeholders
    # for the message are also called message
    message = f"You are now logged in with the e-mail {form["email"]}"
    link = flask.url_for("dashboard")
    homebuttontext = "To dashboard"
    response: flask.Response = flask.make_response(
        flask.render_template("messageonebutton.html", title=title, link=link,
                              message=message, homebuttontext=homebuttontext))
    response.set_cookie(key=COOKIE_NAME_LOGIN_TOKEN,
                        value=accountmanager.GetAccountFromEmail(
                            form["email"]).accountid)
    return response

# Remove the cookie from the browser so that no more authorization can
# be done
@app.route("/logout", methods=["GET"])
def logout():
    email = accountmanager.GetAccountFromToken(COOKIE_NAME_LOGIN_TOKEN)
    title = "Log out"
    message = f"The account with the e-mail {email} logged out successfully"
    link = flask.url_for("index")
    homebuttontext = "Back to home page"
    resp = flask.Response(
        flask.render_template("messageonebutton.html", title=title, link=link,
                              message=message, homebuttontext=homebuttontext))
    resp.delete_cookie(COOKIE_NAME_LOGIN_TOKEN)
    return resp

# ALL events that have been created. Even the ones from other users
@app.route("/events", methods=["GET", "POST"])
def events():
    if flask.request.method == "GET":
        loggedin: bool = flask.request.cookies.get(COOKIE_NAME_LOGIN_TOKEN) is not None
        events: list[eventmanager.Event] = eventmanager.GetAllEvents()
        if not events:
            title = "Events"
            message = "No Events have been created"
            link = flask.url_for("root")
            homebuttontext = gethomebuttontext()
            return flask.render_template("messageonebutton.html", title=title,
                                         message=message, link=link,
                                         homebuttontext=homebuttontext)

        for event in events:
            event.epoch = eventmanager.EpochToNormalTime(event.epoch)
            event.eventtype = eventmanager.GetReadableEventType(event.eventtype)
        def getorganizer(event: eventmanager.Event) -> str:
            account = accountmanager.GetAccountFromEmail(event.organizeremail)
            event.description = event.description.replace(";;;", ",")
            return f"{account.firstname} {account.lastname}"
        # isredirect is set on /createentry
        # if entrymanager.DidAccountAlreadyEnter()
        isredirect = flask.request.args.get("isredirect")
        homebuttontext = gethomebuttontext()
        return flask.render_template("events.html", events=events,
                                     list=list, loggedin=loggedin,
                                     getorganizer=getorganizer,
                                     enumerate=enumerate,
                                     eventmanager=eventmanager,
                                     isredirect=isredirect,
                                     homebuttontext=homebuttontext)

    accountid = flask.request.cookies[COOKIE_NAME_LOGIN_TOKEN]

    # All of this gets executed if the request method is POST.
    # The only thing passed by the form is the button that holds the
    # eventid in it's name
    eventid = list(flask.request.form.keys())[0]
    if entrymanager.DidAccountAlreadyEnter(accountid, eventid):
        return flask.redirect(flask.url_for("events", isredirect=True))

    entrymanager.SaveInCSV(accountid, eventid)

    title = "Events"
    message = f"You have successfully registered to '{eventmanager.GetEventFromId(eventid).eventname}'"
    backlink = flask.url_for("events")
    backbuttontext = "Back to all events"
    homebuttontext = gethomebuttontext()
    return flask.render_template("messagetwobuttons.html", title=title,
                                 message=message, backlink=backlink,
                                 backbuttontext=backbuttontext,
                                 homebuttontext=homebuttontext)

# This just gathers all of the necessary data like the email,
# and eventname and returns it as a dict
def FinishCreateEvent(cookies: dict, form: dict[str, str]) -> dict[str, str]:
    # * Note: The datetime-local input is in the ISO860 format.
    # * But the datetime object doesn't return a timezone anyway. * That means that the date will be saved as "yyyy-mm-ddThh:mm"
    # * (Apparently the T is supposed to be a seperator)
    organizertoken = cookies[COOKIE_NAME_LOGIN_TOKEN]
    organizeremail = accountmanager.GetAccountFromToken(organizertoken).email

    f = lambda s: form[s]
    eventname = f(eventmanager.CSVHeader.NAME)
    epoch: float = eventmanager.InputTimeToEpoch(f("datetime"))
    description = f(eventmanager.CSVHeader.DESCRIPTION).replace(",", ";;;")
    eventtype = f(eventmanager.CSVHeader.EVENTTYPE)

    # The data of a place is dependent on eventmanager.EventType or
    # eventmanager.Event.eventtype
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

    # Better readability
    h = eventmanager.CSVHeader
    # The only header that isn't being returned is the id that gets
    # created by eventmanger
    return { h.NAME: eventname, h.EPOCH: epoch, h.EVENTTYPE: eventtype,
             h.ORGANIZER_EMAIL: organizeremail, h.COUNTRY: country, h.CITY: city,
             h.ZIPCODE: zipcode, h.STREET: street, h.HOUSENUMBER: housenumber,
             h.DESCRIPTION: description }

# Create a new event
@app.route("/createevent", methods=["GET", "POST"])
def createevent():
    if flask.request.method == "GET":
        homebuttontext = gethomebuttontext()
        return flask.render_template("createevent.html",
                                     EventType=eventmanager.EventType,
                                     formlink=flask.url_for("createevent"),
                                     ismodify=False,
                                     eventtype = eventmanager.EventType.ON_SITE,
                                     homebuttontext=homebuttontext)
    form: dict[str, str] = dict(flask.request.form)
    eventdata: dict = FinishCreateEvent(flask.request.cookies, form)
    try:
        pass
        eventmanager.CreateEventFromForm(*eventdata.values())
    except errors.EventAlreadyExistsError:
        title = "Error"
        message = "The event already exists"
        backlink = flask.url_for("createevent")
        backbuttontext = "Back to the event creation"
        homebuttontext = gethomebuttontext()
        return flask.render_template("messagetwobuttons.html", title=title,
                                     message=message, backlink=backlink,
                                     backbuttontext=backbuttontext,
                                     homebuttontext=homebuttontext)

    eventname = form.get(eventmanager.CSVHeader.NAME)
    token = flask.request.cookies.get(COOKIE_NAME_LOGIN_TOKEN)
    organizeremail = accountmanager.GetAccountFromToken(token).email
    title="Event creation"
    message = f"The new event '{eventname}' has been created with the e-mail {organizeremail}"
    backlink = flask.url_for("events")
    backbuttontext = "To the events"
    homebuttontext = gethomebuttontext()
    return flask.render_template("messagetwobuttons.html", title=title,
                                 message=message, backlink=backlink,
                                 backbuttontext=backbuttontext,
                                 homebuttontext=homebuttontext)

# Every event that the user has entried in
@app.route("/entries", methods=["GET", "POST"])
def entries():
    if flask.request.method == "GET":
        accountid = flask.request.cookies[COOKIE_NAME_LOGIN_TOKEN]
        events: list[eventmanager.Event] = entrymanager.GetAllEntriedEventsOfAccount(accountid)

        if not events:
            title = "Error"
            message = "You haven't made an entry to an event yet"
            backlink = flask.url_for("events")
            backbuttontext = "To all Events"
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

        homebuttontext = gethomebuttontext()
        return flask.render_template(
                "entries.html", events=events, enumerate=enumerate,
                loggedin=loggedin, eventmanager=eventmanager, list=list,
                getorganizer=getorganizer, homebuttontext=homebuttontext)


    eventid = list(flask.request.form.keys())[0]
    accountid = flask.request.cookies[COOKIE_NAME_LOGIN_TOKEN]
    entrymanager.DeleteEntry(accountid, eventid)

    title = "Entries"
    message = f"Your entry to the event '{eventmanager.GetEventFromId(eventid).eventname}' has been deleted successfully"
    backlink = flask.url_for("entries")
    backbuttontext = "Back to your entries"
    homebuttontext = gethomebuttontext()
    return flask.render_template("messagetwobuttons.html", title=title,
                                 message=message, backlink=backlink,
                                 backbuttontext=backbuttontext,
                                 homebuttontext=homebuttontext)

# All events created by the user
@app.route("/myevents", methods=["GET", "POST"])
def myevents():
    if flask.request.method == "GET":
        token = flask.request.cookies[COOKIE_NAME_LOGIN_TOKEN]
        email = accountmanager.GetAccountFromToken(token).email
        title = "My events"
        try:
            createdevents = eventmanager.GetAllEventsCreatedByOrganizer(email)
        except errors.AccountHasNoEventsError:
            message = "You haven't created any Events"
            backlink = flask.url_for("createevent")
            backbuttontext = "Create an event"
            homebuttontext = gethomebuttontext()
            return flask.render_template("messagetwobuttons.html", title=title,
                                         message=message, backlink=backlink,
                                         backbuttontext=backbuttontext,
                                         homebuttontext=homebuttontext)
        for event in createdevents:
            event.epoch = eventmanager.EpochToNormalTime(event.epoch)
            event.eventtype = eventmanager.GetReadableEventType(event.eventtype)

        homebuttontext = gethomebuttontext()
        return flask.render_template("myevents.html", list=list,
                                     events=createdevents, enumerate=enumerate,
                                     eventmanager=eventmanager,
                                     homebuttontext=homebuttontext)

    # A POST request is sent to delete the event
    eventid = list(flask.request.form.keys())[0]
    eventmanager.DeleteEvent(eventid)
    title = "My events"
    message = "The event has been deleted successfully."
    backlink = flask.url_for("myevents")
    backbuttontext = "Back to your events"
    homebuttontext = gethomebuttontext()
    return flask.render_template("messagetwobuttons.html", title=title,
                                 message=message, backlink=backlink,
                                 backbuttontext=backbuttontext,
                                 homebuttontext=homebuttontext)

@app.route("/modifyevent", methods=["GET", "POST"])
def modifyevent():
    # Note: The id of the event is the first and only in the args of the
    # GET request.
    # The event data is passed as form
    if flask.request.method == "GET":
        eventid = list(flask.request.args.keys())[0]
        originalevent = eventmanager.GetEventFromId(eventid)
        # So that I have to type less
        headers = eventmanager.CSVHeader
        eventdict = dict(zip(headers.AsList(), list(originalevent)))
        isonline = eventdict.get(headers.EVENTTYPE) == eventmanager.EventType.ONLINE
        eventdict[headers.EPOCH] = eventmanager.EpochToInputTime(eventdict[headers.EPOCH])
        homebuttontext = gethomebuttontext()
        # createevent.html is being reused because the inputs are the same
        return flask.render_template("createevent.html",
                                     ismodify=True, eventid=eventid,
                                     EventType=eventmanager.EventType,
                                     formlink=flask.url_for("modifyevent"),
                                     isonline = isonline,
                                     homebuttontext=homebuttontext,
                                     formatedTime=eventdict[headers.EPOCH],
                                     **eventdict)


    eventdata: dict = FinishCreateEvent(dict(flask.request.cookies),
                                        dict(flask.request.form))
    eventid = dict(flask.request.form).get("eventid")
    eventdata.update({eventmanager.CSVHeader.EVENTID: eventid})
    event = eventmanager.Event.InitFromDict(eventdata)
    eventmanager.ModifyEvent(event)

    title = "My events"
    message = f"The event '{eventdata["name"]}' has been updated successfully"
    backlink = flask.url_for("myevents")
    backbuttontext = "Back to your events"
    homebuttontext = gethomebuttontext()

    return flask.render_template("messagetwobuttons.html", title=title,
                                 message=message, backlink=backlink,
                                 backbuttontext=backbuttontext,
                                 homebuttontext=homebuttontext)


@app.before_request
def checkIfUserIsLoggedIn():
    token: str | None = flask.request.cookies.get(COOKIE_NAME_LOGIN_TOKEN)
    allowedSitesIfLoggedOut: list[str] = ["index","register","login","events"]
    # The if statement prevents that a page that may not even exist,
    # like /abcdef for example, returns an error code of 404, but
    # redirects to the home page or the dashboard
    loggedin = bool(token)
    if not loggedin and flask.request.endpoint not in allowedSitesIfLoggedOut:
        return flask.redirect(flask.url_for("index"))
    allowedSiteIfLoggedIn: list[str] = ["dashboard","register","login","logout",
                                        "events","createevent","entries",
                                        "myevents","modifyevent"]
    if loggedin and flask.request.endpoint not in allowedSiteIfLoggedIn:
        return flask.redirect(flask.url_for("dashboard"))
    # Nothing is being returned


if __name__ == "__main__":
    DEFAULT_HTTP_PORT = 80
    app.run(port=DEFAULT_HTTP_PORT, debug=True)

