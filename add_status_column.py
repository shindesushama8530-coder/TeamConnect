"""
Migration script to add status column to teams table
"""
from database.db import get_connection

connection = get_connection()
cursor = connection.cursor()

try:
    # Add status column if it doesn't exist
    cursor.execute(
        """
        ALTER TABLE teams
        ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'Open'
        """
    )
    
    # Update existing teams to have 'Open' status
    cursor.execute(
        """
        UPDATE teams
        SET status = 'Open'
        WHERE status IS NULL
        """
    )
    
    connection.commit()
    print("Status column added successfully to teams table!")
    
except Exception as e:
    print(f"Error: {e}")
    connection.rollback()

cursor.close()
connection.close()
