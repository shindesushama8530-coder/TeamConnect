"""
Migration script to add team leaders as members of their own teams
"""
from database.db import get_connection

connection = get_connection()
cursor = connection.cursor()

try:
    # Check for teams where leader is not in team_members
    cursor.execute(
        """
        SELECT t.id, t.team_name, t.created_by
        FROM teams t
        WHERE NOT EXISTS (
            SELECT 1 FROM team_members tm 
            WHERE tm.team_id = t.id AND tm.user_id = t.created_by
        )
        """
    )

    teams_without_leader = cursor.fetchall()
    
    if teams_without_leader:
        print(f"Found {len(teams_without_leader)} teams where leader is not a member")
        
        for team_id, team_name, created_by in teams_without_leader:
            print(f"Adding leader (user_id={created_by}) to team: {team_name}")
            cursor.execute(
                """
                INSERT INTO team_members (team_id, user_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
                """,
                (team_id, created_by)
            )
        
        connection.commit()
        print("Migration completed!")
    else:
        print("All team leaders are already members of their teams")
    
except Exception as e:
    print(f"Error: {e}")
    connection.rollback()

cursor.close()
connection.close()
