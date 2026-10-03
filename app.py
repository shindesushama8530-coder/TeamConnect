from flask import Flask, render_template
from routes.auth import auth
from routes.profile import profile
from routes.teams import teams
from routes.requests import requests
from routes.messages import messages

app = Flask(__name__)

app.secret_key = "teamconnect_secret_key"

app.register_blueprint(auth)
app.register_blueprint(profile)
app.register_blueprint(teams)
app.register_blueprint(requests)
app.register_blueprint(messages)

@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)