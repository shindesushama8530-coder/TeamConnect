from flask import Blueprint, render_template, request, redirect, url_for, session
from database.db import get_connection

teams = Blueprint("teams", __name__)


# --------------------------------
# CREATE TEAM
# --------------------------------

@teams.route("/create-team", methods=["GET", "POST"])
def create_team():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        team_name = request.form["team_name"]
        event = request.form["event"]
        description = request.form["description"]
        required_skills = request.form["required_skills"]
        team_size = request.form["team_size"]

        user_id = session["user_id"]

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO teams
            (team_name, event, description, required_skills, team_size, created_by)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                team_name,
                event,
                description,
                required_skills,
                team_size,
                user_id
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return "Team created successfully!"

    return render_template("create_team.html")


# --------------------------------
# FIND TEAMS
# --------------------------------

@teams.route("/find-teams")
def find_teams():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id,
               team_name,
               event,
               description,
               required_skills,
               team_size
        FROM teams
        ORDER BY created_at DESC
        """
    )

    teams_list = cursor.fetchall()

    # Get teams where user is a member
    cursor.execute(
        """
        SELECT team_id
        FROM team_members
        WHERE user_id = %s
        """,
        (user_id,)
    )

    member_teams = [row[0] for row in cursor.fetchall()]

    # Also check if user is team leader
    cursor.execute(
        """
        SELECT id
        FROM teams
        WHERE created_by = %s
        """,
        (user_id,)
    )

    leader_teams = [row[0] for row in cursor.fetchall()]

    cursor.close()
    connection.close()

    return render_template(
        "find_teams.html",
        teams=teams_list,
        member_teams=member_teams,
        leader_teams=leader_teams
    )