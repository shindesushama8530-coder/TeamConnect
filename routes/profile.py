from flask import Blueprint, render_template, redirect, url_for, session
from database.db import get_connection

profile = Blueprint("profile", __name__)


@profile.route("/profile")
def view_profile():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT name, email, department, year, skills, interests, bio
        FROM users
        WHERE id = %s
        """,
        (user_id,)
    )

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template(
        "profile.html",
        user=user
    )