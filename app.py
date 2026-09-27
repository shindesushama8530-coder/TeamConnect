from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/find-teams")
def find_teams():

    teams = [
        {
            "name": "AI Innovators",
            "event": "Hackathon",
            "skills": "Python, AI, Machine Learning",
            "members": "3 / 4"
        },
        {
            "name": "Web Warriors",
            "event": "Web Development Competition",
            "skills": "HTML, CSS, Flask",
            "members": "2 / 4"
        },
        {
            "name": "Data Masters",
            "event": "Data Science Project",
            "skills": "Python, Data Analysis",
            "members": "3 / 5"
        }
    ]

    return render_template("find_teams.html", teams=teams)


if __name__ == "__main__":
    app.run(debug=True)