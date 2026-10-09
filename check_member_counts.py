from database.db import get_connection

connection = get_connection()
cursor = connection.cursor()

# Check team member counts
cursor.execute(
    """
    SELECT t.id, t.team_name, t.team_size, 
           COALESCE(COUNT(tm.id), 0) as member_count
    FROM teams t
    LEFT JOIN team_members tm ON t.id = tm.team_id
    GROUP BY t.id, t.team_name, t.team_size
    ORDER BY t.id
    """
)

print("Team Member Counts:")
print("-" * 60)
for row in cursor.fetchall():
    team_id, team_name, team_size, member_count = row
    print(f"ID: {team_id} | {team_name} | {member_count}/{team_size} members")

cursor.close()
connection.close()
