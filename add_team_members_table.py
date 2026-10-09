"""
Migration script to add team_members table
"""
from database.db import get_connection

connection = get_connection()
cursor = connection.cursor()

try:
    # Create team_members table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS team_members (
            id SERIAL PRIMARY KEY,
            team_id INTEGER REFERENCES teams(id) ON DELETE CASCADE,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    
    connection.commit()
    print("team_members table created successfully!")
    
    # Check if we need to migrate existing join_requests
    cursor.execute(
        """
        SELECT COUNT(*) FROM join_requests WHERE status = 'Approved'
        """
    )
    approved_count = cursor.fetchone()[0]
    
    if approved_count > 0:
        print(f"Found {approved_count} approved join requests. Migrating to team_members...")
        
        # Migrate approved join_requests to team_members
        cursor.execute(
            """
            INSERT INTO team_members (team_id, user_id, joined_at)
            SELECT team_id, user_id, created_at
            FROM join_requests
            WHERE status = 'Approved'
            ON CONFLICT DO NOTHING
            """
        )
        
        connection.commit()
        print("Migration completed!")
    
except Exception as e:
    print(f"Error: {e}")
    connection.rollback()

cursor.close()
connection.close()
