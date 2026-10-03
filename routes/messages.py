from flask import Blueprint, render_template, request, redirect, url_for, session
from database.db import get_connection

messages = Blueprint("messages", __name__)


# --------------------------------
# SEND MESSAGE
# --------------------------------

@messages.route("/send-message/<int:team_id>/<int:receiver_id>", methods=["GET", "POST"])
def send_message(team_id, receiver_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        message_content = request.form["message"]
        sender_id = session["user_id"]

        # Verify sender is a team member
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id
            FROM team_members
            WHERE team_id = %s AND user_id = %s
            """,
            (team_id, sender_id)
        )

        sender_member = cursor.fetchone()

        # Also check if sender is team leader
        cursor.execute(
            """
            SELECT created_by
            FROM teams
            WHERE id = %s
            """,
            (team_id,)
        )

        team_leader = cursor.fetchone()

        if not sender_member and (not team_leader or team_leader[0] != sender_id):
            cursor.close()
            connection.close()
            return "You are not a member of this team!"

        # Verify receiver is a team member
        cursor.execute(
            """
            SELECT id
            FROM team_members
            WHERE team_id = %s AND user_id = %s
            """,
            (team_id, receiver_id)
        )

        receiver_member = cursor.fetchone()

        if not receiver_member and (not team_leader or team_leader[0] != receiver_id):
            cursor.close()
            connection.close()
            return "Receiver is not a member of this team!"

        # Send message
        cursor.execute(
            """
            INSERT INTO messages
            (sender_id, receiver_id, team_id, message)
            VALUES (%s, %s, %s, %s)
            """,
            (sender_id, receiver_id, team_id, message_content)
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("messages.view_messages", team_id=team_id))

    return render_template("send_message.html", team_id=team_id, receiver_id=receiver_id)


# --------------------------------
# VIEW MESSAGES
# --------------------------------

@messages.route("/messages/<int:team_id>")
def view_messages(team_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    connection = get_connection()
    cursor = connection.cursor()

    # Verify user is a team member or leader
    cursor.execute(
        """
        SELECT id
        FROM team_members
        WHERE team_id = %s AND user_id = %s
        """,
        (team_id, user_id)
    )

    is_member = cursor.fetchone()

    cursor.execute(
        """
        SELECT created_by
        FROM teams
        WHERE id = %s
        """,
        (team_id,)
    )

    team_leader = cursor.fetchone()

    if not is_member and (not team_leader or team_leader[0] != user_id):
        cursor.close()
        connection.close()
        return "You are not a member of this team!"

    # Get all messages for this team involving the current user
    cursor.execute(
        """
        SELECT
            messages.id,
            sender.name AS sender_name,
            receiver.name AS receiver_name,
            messages.message,
            messages.created_at,
            CASE WHEN messages.sender_id = %s THEN 'sent' ELSE 'received' END AS direction
        FROM messages
        JOIN users AS sender ON messages.sender_id = sender.id
        JOIN users AS receiver ON messages.receiver_id = receiver.id
        WHERE messages.team_id = %s
        AND (messages.sender_id = %s OR messages.receiver_id = %s)
        ORDER BY messages.created_at DESC
        """,
        (user_id, team_id, user_id, user_id)
    )

    messages_list = cursor.fetchall()

    # Get team members for messaging
    cursor.execute(
        """
        SELECT DISTINCT users.id, users.name
        FROM team_members
        JOIN users ON team_members.user_id = users.id
        WHERE team_members.team_id = %s AND team_members.user_id != %s
        """,
        (team_id, user_id)
    )

    team_members = cursor.fetchall()

    # Add team leader if not already in list
    if team_leader and team_leader[0] != user_id:
        cursor.execute(
            """
            SELECT id, name
            FROM users
            WHERE id = %s
            """,
            (team_leader[0],)
        )
        leader_info = cursor.fetchone()
        if leader_info:
            team_members.append(leader_info)

    cursor.close()
    connection.close()

    return render_template(
        "messages.html",
        messages=messages_list,
        team_members=team_members,
        team_id=team_id
    )
