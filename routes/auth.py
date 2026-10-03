from flask import Blueprint, render_template, request, redirect, url_for, session
from database.db import get_connection

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        department = request.form["department"]
        year = request.form["year"]
        skills = request.form["skills"]

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO users
            (name, email, password, department, year, skills)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                name,
                email,
                password,
                department,
                year,
                skills
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return "Registration successful!"

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, name, password
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user is not None:

            if user[2] == password:

                session["user_id"] = user[0]
                session["user_name"] = user[1]

                return redirect(url_for("auth.dashboard"))

            else:
                return "Incorrect password!"

        else:
            return "User not found!"

    return render_template("login.html")


@auth.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    return render_template(
        "dashboard.html",
        name=session["user_name"]
    )