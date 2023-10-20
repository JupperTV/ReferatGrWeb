import flask

app = flask.Flask(__name__)

@app.route("/index")
def index():
    return flask.render_template("index.html")

@app.route("/login")
def login():
    return flask.render_template("login.html")

@app.route("/register")
def register():
    return flask.render_template("register.html")

@app.route("/registerfinished")
def registerfinished():
    argstuff: dict = flask.request.args
    formstuff: dict = flask.request.form
    print(f"argstuff: {argstuff}\nformstuff: {formstuff}")

