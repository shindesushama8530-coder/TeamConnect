from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.db import get_connection

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        department = request.form.get("department", "").strip()
        year = request.form.get("year", "").strip()
        skills = request.form.get("skills", "").strip()

        if not name or not email or not password:
            return render_template("register.html", error="Please fill in all required fields!")

        try:
            connection = get_connection()
            cursor = connection.cursor()

            # Check if email already exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                cursor.close()
                connection.close()
                return render_template("register.html", error="An account with this email already exists!")

            cursor.execute(
                """
                INSERT INTO users
                (name, email, password, department, year, skills)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (name, email, password, department, year, skills)
            )

            connection.commit()
            cursor.close()
            connection.close()

            return redirect(url_for("auth.login", success="Account created successfully! Please sign in."))
        except Exception as e:
            return render_template("register.html", error=f"Registration failed: {str(e)}")

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    error = None
    success = request.args.get("success")

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        try:
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
                    session["user_email"] = email
                    return redirect(url_for("auth.dashboard"))
                else:
                    return render_template("login.html", error="Incorrect password! Please try again.")
            else:
                return render_template("login.html", error="No account found with this email address.")
        except Exception as e:
            return render_template("login.html", error=f"Database connection error: {str(e)}")

    return render_template("login.html", error=error, success=success)


@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login", success="You have been safely signed out."))


@auth.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    user_name = session.get("user_name", "Student")

    # Fetch stats for user
    connection = get_connection()
    cursor = connection.cursor()

    # User details
    cursor.execute("SELECT department, year, skills FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()

    # Count of joined/created teams
    cursor.execute("""
        SELECT COUNT(DISTINCT t.id)
        FROM teams t
        LEFT JOIN team_members tm ON t.id = tm.team_id
        WHERE t.created_by = %s OR tm.user_id = %s
    """, (user_id, user_id))
    teams_count = cursor.fetchone()[0]

    # Count of pending join requests sent
    cursor.execute("""
        SELECT COUNT(*)
        FROM join_requests
        WHERE user_id = %s AND status = 'Pending'
    """, (user_id,))
    my_pending_requests = cursor.fetchone()[0]

    # Count of incoming requests for user's teams
    cursor.execute("""
        SELECT COUNT(jr.id)
        FROM join_requests jr
        JOIN teams t ON jr.team_id = t.id
        WHERE t.created_by = %s AND jr.status = 'Pending'
    """, (user_id,))
    incoming_requests_count = cursor.fetchone()[0]

    # Fetch recent teams to display as recommendations
    cursor.execute("""
        SELECT t.id, t.team_name, t.event, t.required_skills, t.team_size,
               COALESCE(COUNT(tm.id), 0) as member_count
        FROM teams t
        LEFT JOIN team_members tm ON t.id = tm.team_id
        GROUP BY t.id, t.team_name, t.event, t.required_skills, t.team_size
        ORDER BY t.created_at DESC
        LIMIT 4
    """)
    recommended_teams = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "dashboard.html",
        name=user_name,
        user=user_data,
        teams_count=teams_count,
        pending_requests_count=my_pending_requests,
        incoming_requests_count=incoming_requests_count,
        recommended_teams=recommended_teams
    )