from flask import Blueprint, render_template, redirect, url_for, session, request, flash
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


@profile.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    connection = get_connection()
    cursor = connection.cursor()

    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        department = request.form.get("department")
        year = request.form.get("year")
        skills = request.form.get("skills")
        interests = request.form.get("interests")
        bio = request.form.get("bio")

        # Update user profile
        cursor.execute(
            """
            UPDATE users
            SET name = %s, department = %s, year = %s, skills = %s, interests = %s, bio = %s
            WHERE id = %s
            """,
            (name, department, year, skills, interests, bio, user_id)
        )

        connection.commit()
        cursor.close()
        connection.close()

        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile.view_profile"))

    # GET request - fetch current user data
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

    return render_template("edit_profile.html", user=user)