from flask import Blueprint, render_template, redirect, url_for, session
from database.db import get_connection

requests = Blueprint("requests", __name__)


# --------------------------------
# REQUEST TO JOIN TEAM
# --------------------------------

@requests.route("/join-team/<int:team_id>")
def join_team(team_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    connection = get_connection()
    cursor = connection.cursor()

    # Check if user is already a team member
    cursor.execute(
        """
        SELECT id
        FROM team_members
        WHERE team_id = %s AND user_id = %s
        """,
        (team_id, user_id)
    )

    existing_member = cursor.fetchone()

    if existing_member:
        cursor.close()
        connection.close()
        return redirect(url_for("teams.find_teams", error="You are already a member of this team!"))

    # Check if request already exists
    cursor.execute(
        """
        SELECT id
        FROM join_requests
        WHERE team_id = %s
        AND user_id = %s
        """,
        (team_id, user_id)
    )

    existing_request = cursor.fetchone()

    if existing_request:
        cursor.close()
        connection.close()
        return redirect(url_for("teams.find_teams", error="You have already requested to join this team!"))

    # Check team capacity
    cursor.execute(
        """
        SELECT team_size
        FROM teams
        WHERE id = %s
        """,
        (team_id,)
    )

    team_data = cursor.fetchone()

    if team_data is None:
        cursor.close()
        connection.close()
        return redirect(url_for("teams.find_teams", error="Team not found!"))

    max_team_size = team_data[0]

    # Count current team members
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM team_members
        WHERE team_id = %s
        """,
        (team_id,)
    )

    current_member_count = cursor.fetchone()[0]

    if current_member_count >= max_team_size:
        cursor.close()
        connection.close()
        return redirect(url_for("teams.find_teams", error="Team is already full! Cannot join."))

    # Insert new request
    cursor.execute(
        """
        INSERT INTO join_requests
        (team_id, user_id, status)
        VALUES (%s, %s, %s)
        """,
        (team_id, user_id, "Pending")
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("teams.find_teams", success="Join request sent successfully!"))


# --------------------------------
# VIEW JOIN REQUESTS
# --------------------------------

@requests.route("/requests")
def view_requests():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            join_requests.id,
            users.name,
            users.email,
            users.skills,
            teams.team_name,
            join_requests.status
        FROM join_requests
        JOIN users
            ON join_requests.user_id = users.id
        JOIN teams
            ON join_requests.team_id = teams.id
        WHERE teams.created_by = %s
        ORDER BY join_requests.created_at DESC
        """,
        (user_id,)
    )

    requests_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "requests.html",
        requests=requests_list,
        success=request.args.get("success"),
        error=request.args.get("error")
    )


   # --------------------------------
# ACCEPT REQUEST
# --------------------------------

@requests.route("/accept-request/<int:request_id>")
def accept_request(request_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    connection = get_connection()
    cursor = connection.cursor()

    # Get team ID and student ID from the request
    cursor.execute(
        """
        SELECT team_id, user_id
        FROM join_requests
        WHERE id = %s
        """,
        (request_id,)
    )

    request_data = cursor.fetchone()

    if request_data is None:
        cursor.close()
        connection.close()
        return redirect(url_for("requests.view_requests", error="Request not found!"))

    team_id = request_data[0]
    user_id = request_data[1]

    # Check if user is already a team member
    cursor.execute(
        """
        SELECT id
        FROM team_members
        WHERE team_id = %s AND user_id = %s
        """,
        (team_id, user_id)
    )

    existing_member = cursor.fetchone()

    if existing_member:
        cursor.close()
        connection.close()
        return redirect(url_for("requests.view_requests", error="User is already a team member!"))

    # Check current team size
    cursor.execute(
        """
        SELECT team_size
        FROM teams
        WHERE id = %s
        """,
        (team_id,)
    )

    team_data = cursor.fetchone()

    if team_data is None:
        cursor.close()
        connection.close()
        return redirect(url_for("requests.view_requests", error="Team not found!"))

    max_team_size = team_data[0]

    # Count current team members
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM team_members
        WHERE team_id = %s
        """,
        (team_id,)
    )

    current_member_count = cursor.fetchone()[0]

    if current_member_count >= max_team_size:
        cursor.close()
        connection.close()
        return redirect(url_for("requests.view_requests", error="Team is already full!"))

    # Change request status to Accepted
    cursor.execute(
        """
        UPDATE join_requests
        SET status = 'Accepted'
        WHERE id = %s
        """,
        (request_id,)
    )

    # Add student to team members
    cursor.execute(
        """
        INSERT INTO team_members
        (team_id, user_id)
        VALUES (%s, %s)
        """,
        (team_id, user_id)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("requests.view_requests", success="Request accepted successfully!"))


# --------------------------------
# REJECT REQUEST
# --------------------------------

@requests.route("/reject-request/<int:request_id>")
def reject_request(request_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE join_requests
        SET status = 'Rejected'
        WHERE id = %s
        """,
        (request_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("requests.view_requests", success="Request rejected successfully!"))