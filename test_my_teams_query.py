from database.db import get_connection

# Simulate user_id = 1 (Sushama)
user_id = 1

connection = get_connection()
cursor = connection.cursor()

# Get teams where user is a member or leader (same query as my_teams)
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
    WHERE t.created_by = %s 
       OR t.id IN (SELECT team_id FROM team_members WHERE user_id = %s)
    GROUP BY t.id, t.team_name, t.event, t.description, t.required_skills, t.team_size, t.status, t.created_by
    ORDER BY t.created_at DESC
"""

cursor.execute(query, (user_id, user_id, user_id))
teams_list = cursor.fetchall()

print("My Teams Query Results:")
print("-" * 100)

for team in teams_list:
    team_id, team_name, event, description, required_skills, team_size, manual_status, created_by, member_count, is_leader = team
    
    # Calculate automatic status
    if member_count >= team_size:
        auto_status = "Full"
    elif member_count >= team_size - 1:
        auto_status = "Almost Full"
    else:
        auto_status = "Open"
    
    print(f"Team: {team_name} (ID: {team_id})")
    print(f"  Members: {member_count}/{team_size}")
    print(f"  Auto Status: {auto_status}")
    print(f"  Is Leader: {is_leader}")
    print()

cursor.close()
connection.close()
