from database.db import get_connection

connection = get_connection()
cursor = connection.cursor()

# Check team 9 details
cursor.execute(
    """
    SELECT t.id, t.team_name, t.team_size
    FROM teams t
    WHERE t.id = 9
    """
)

team = cursor.fetchone()
if team:
    team_id, team_name, team_size = team
    print(f"Team: {team_name} (ID: {team_id})")
    print(f"Team Size: {team_size}")
    
    # Count members
    cursor.execute(
        """
        SELECT COUNT(*) FROM team_members WHERE team_id = 9
        """
    )
    member_count = cursor.fetchone()[0]
    print(f"Member Count: {member_count}")
    
    # List all members
    cursor.execute(
        """
        SELECT u.name, u.id, tm.joined_at
        FROM team_members tm
        JOIN users u ON tm.user_id = u.id
        WHERE tm.team_id = 9
        """
    )
    members = cursor.fetchall()
    print("\nMembers:")
    for name, user_id, joined_at in members:
        print(f"  - {name} (ID: {user_id}) joined at {joined_at}")
    
    # Check join_requests for this team
    cursor.execute(
        """
        SELECT u.name, jr.status
        FROM join_requests jr
        JOIN users u ON jr.user_id = u.id
        WHERE jr.team_id = 9
        """
    )
    requests = cursor.fetchall()
    print("\nJoin Requests:")
    for name, status in requests:
        print(f"  - {name}: {status}")

cursor.close()
connection.close()
