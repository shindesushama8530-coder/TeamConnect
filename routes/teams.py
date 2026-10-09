from flask import Blueprint, render_template, request, redirect, url_for, session
from database.db import get_connection

teams = Blueprint("teams", __name__)


# --------------------------------
# DELETE TEAM
# --------------------------------

@teams.route("/delete-team/<int:team_id>", methods=["POST"])
def delete_team(team_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    connection = get_connection()
    cursor = connection.cursor()

    # Check if user is the team leader
    cursor.execute(
        """
        SELECT created_by
        FROM teams
        WHERE id = %s
        """,
        (team_id,)
    )

    team = cursor.fetchone()

    if team is None:
        cursor.close()
        connection.close()
        return "Team not found!"

    if team[0] != user_id:
        cursor.close()
        connection.close()
        return "You are not authorized to delete this team!"

    # Delete team members
    cursor.execute(
        """
        DELETE FROM team_members
        WHERE team_id = %s
        """,
        (team_id,)
    )

    # Delete join requests
    cursor.execute(
        """
        DELETE FROM join_requests
        WHERE team_id = %s
        """,
        (team_id,)
    )

    # Delete messages
    cursor.execute(
        """
        DELETE FROM messages
        WHERE team_id = %s
        """,
        (team_id,)
    )

    # Delete the team
    cursor.execute(
        """
        DELETE FROM teams
        WHERE id = %s
        """,
        (team_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("teams.find_teams"))


# --------------------------------
# REMOVE MEMBER
# --------------------------------

@teams.route("/remove-member/<int:team_id>/<int:member_id>", methods=["POST"])
def remove_member(team_id, member_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    connection = get_connection()
    cursor = connection.cursor()

    # Check if user is the team leader
    cursor.execute(
        """
        SELECT created_by
        FROM teams
        WHERE id = %s
        """,
        (team_id,)
    )

    team = cursor.fetchone()

    if team is None:
        cursor.close()
        connection.close()
        return redirect(url_for("messages.view_messages", team_id=team_id, error="Team not found!"))

    if team[0] != user_id:
        cursor.close()
        connection.close()
        return redirect(url_for("messages.view_messages", team_id=team_id, error="You are not authorized to remove members!"))

    # Prevent leader from removing themselves
    if member_id == user_id:
        cursor.close()
        connection.close()
        return redirect(url_for("messages.view_messages", team_id=team_id, error="You cannot remove yourself from the team!"))

    # Remove the member
    cursor.execute(
        """
        DELETE FROM team_members
        WHERE team_id = %s AND user_id = %s
        """,
        (team_id, member_id)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("messages.view_messages", team_id=team_id, success="Member removed successfully!"))


# --------------------------------
# MY TEAMS
# --------------------------------

@teams.route("/my-teams", methods=["GET", "POST"])
def my_teams():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    connection = get_connection()
    cursor = connection.cursor()

    # Get teams where user is a member or leader
    query = """
        SELECT t.id,
               t.team_name,
               t.event,
               t.description,
               t.required_skills,
               t.team_size,
               t.status,
               t.created_by,
               COALESCE(COUNT(tm.id), 0) as member_count,
               CASE WHEN t.created_by = %s THEN true ELSE false END as is_leader
        FROM teams t
        LEFT JOIN team_members tm ON t.id = tm.team_id
        WHERE t.created_by = %s OR tm.user_id = %s
        GROUP BY t.id, t.team_name, t.event, t.description, t.required_skills, t.team_size, t.status, t.created_by
        ORDER BY t.created_at DESC
    """

    cursor.execute(query, (user_id, user_id, user_id))
    teams_list = cursor.fetchall()

    # Calculate automatic status for each team
    teams_with_status = []
    for team in teams_list:
        team_id, team_name, event, description, required_skills, team_size, manual_status, created_by, member_count, is_leader = team
        
        # Calculate automatic status
        if member_count >= team_size:
            auto_status = "Full"
        elif member_count >= team_size - 1:
            auto_status = "Almost Full"
        else:
            auto_status = "Open"
        
        teams_with_status.append({
            'id': team_id,
            'team_name': team_name,
            'event': event,
            'description': description,
            'required_skills': required_skills,
            'team_size': team_size,
            'manual_status': manual_status,
            'created_by': created_by,
            'member_count': member_count,
            'auto_status': auto_status,
            'is_leader': is_leader
        })

    cursor.close()
    connection.close()

    return render_template(
        "my_teams.html",
        teams=teams_with_status,
        success=request.args.get("success"),
        error=request.args.get("error")
    )


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
            (team_name, event, description, required_skills, team_size, created_by, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                team_name,
                event,
                description,
                required_skills,
                team_size,
                user_id,
                'Open'
            )
        )

        connection.commit()

        # Get the newly created team ID
        cursor.execute(
            """
            SELECT id FROM teams
            WHERE created_by = %s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (user_id,)
        )
        team_id = cursor.fetchone()[0]

        # Add the team leader as the first member
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

        return redirect(url_for("teams.find_teams", success="Team created successfully!"))

    return render_template("create_team.html")


# --------------------------------
# FIND TEAMS
# --------------------------------

@teams.route("/find-teams", methods=["GET", "POST"])
def find_teams():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    connection = get_connection()
    cursor = connection.cursor()

    # Get filter values from form
    search_query = request.form.get("search", "") if request.method == "POST" else request.args.get("search", "")
    skills_filter = request.form.get("skills", "") if request.method == "POST" else request.args.get("skills", "")
    year_filter = request.form.get("year", "") if request.method == "POST" else request.args.get("year", "")
    status_filter = request.form.get("status", "") if request.method == "POST" else request.args.get("status", "")

    # Build base query with member count
    query = """
        SELECT t.id,
               t.team_name,
               t.event,
               t.description,
               t.required_skills,
               t.team_size,
               t.status,
               COALESCE(COUNT(tm.id), 0) as member_count
        FROM teams t
        LEFT JOIN team_members tm ON t.id = tm.team_id
        LEFT JOIN users u ON t.created_by = u.id
        WHERE 1=1
    """
    params = []

    # Add search filter (team name or event)
    if search_query:
        query += " AND (t.team_name ILIKE %s OR t.event ILIKE %s)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    # Add skills filter
    if skills_filter:
        query += " AND t.required_skills ILIKE %s"
        params.append(f"%{skills_filter}%")

    # Add year filter
    if year_filter:
        query += " AND u.year ILIKE %s"
        params.append(f"%{year_filter}%")

    query += " GROUP BY t.id, t.team_name, t.event, t.description, t.required_skills, t.team_size, t.status"

    # Add status filter (filter by automatic status)
    if status_filter:
        if status_filter == "Open":
            query += " HAVING (COUNT(tm.id) < t.team_size - 1)"
        elif status_filter == "Almost Full":
            query += " HAVING (COUNT(tm.id) >= t.team_size - 1 AND COUNT(tm.id) < t.team_size)"
        elif status_filter == "Full":
            query += " HAVING (COUNT(tm.id) >= t.team_size)"

    query += " ORDER BY t.created_at DESC"

    cursor.execute(query, params)
    teams_list = cursor.fetchall()

    # Calculate automatic status for each team
    teams_with_status = []
    for team in teams_list:
        team_id, team_name, event, description, required_skills, team_size, manual_status, member_count = team
        
        # Calculate automatic status
        if member_count >= team_size:
            auto_status = "Full"
        elif member_count >= team_size - 1:
            auto_status = "Almost Full"
        else:
            auto_status = "Open"
        
        teams_with_status.append({
            'id': team_id,
            'team_name': team_name,
            'event': event,
            'description': description,
            'required_skills': required_skills,
            'team_size': team_size,
            'manual_status': manual_status,
            'member_count': member_count,
            'auto_status': auto_status
        })

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

    # Get teams where user has pending requests
    cursor.execute(
        """
        SELECT team_id, id
        FROM join_requests
        WHERE user_id = %s AND status = 'Pending'
        """,
        (user_id,)
    )

    pending_requests = {row[0]: row[1] for row in cursor.fetchall()}

    # Get unique years for filter dropdown
    cursor.execute(
        """
        SELECT DISTINCT year
        FROM users
        WHERE year IS NOT NULL
        ORDER BY year
        """
    )
    years = [row[0] for row in cursor.fetchall()]

    cursor.close()
    connection.close()

    return render_template(
        "find_teams.html",
        teams=teams_with_status,
        member_teams=member_teams,
        leader_teams=leader_teams,
        pending_requests=pending_requests,
        years=years,
        search=search_query,
        skills=skills_filter,
        year=year_filter,
        status=status_filter,
        success=request.args.get("success"),
        error=request.args.get("error")
    )