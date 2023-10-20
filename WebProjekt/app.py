#!/usr/bin/python
# Sicherheitshalber einen Shebang einfügen

from os import system # ! NOTIZ: NACHHER LÖSCHEN
system("cls")
del system

import flask  # Das Hauptframework, das hier benutzt wird

import registrationmanager


app = flask.Flask(__name__, static_folder="static", template_folder="static")


@app.route("/", methods=["GET"])
def home():
    return flask.redirect(flask.url_for("index"))

@app.route("/index", methods=["GET"])
def index():
    return flask.render_template("index.html")

@app.route("/login", methods=["GET"])
def login():
    return flask.render_template("login.html")

@app.route("/register", methods=["GET"])
def register():
    return flask.render_template("register.html")

# Hier werden die Daten nach dem Register verarbeitet
@app.route("/finishregister", methods=["GET", "POST"])
def registerfinished():
    if flask.request.method != "POST":
        return flask.redirect(flask.url_for("login"))

    formdata: dict = flask.request.form
    form: str = "<br>".join([f"{k}: {v}" for k, v in formdata.items()])
    return f"formstuff:<br>{form}<br><br>"

# Hier werden die Daten nach dem Login geprüft
@app.route("/checklogin", methods=["GET", "POST"])
def checklogin():
    if flask.request.method != "POST":
        return flask.redirect(flask.url_for("login"))

    formdata: dict = flask.request.form
    form: str = "<br>".join([f"{k}: {v}" for k, v in formdata.items()])
    return f"formstuff:<br>{form}<br><br>"

if __name__ == "__main__":
    DEFAULT_HTTP_PORT = 80  # Zur Vermeidung von Magic Numbers
    app.run(port=DEFAULT_HTTP_PORT, debug=True)


