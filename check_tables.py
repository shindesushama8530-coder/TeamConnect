from database.db import get_connection

connection = get_connection()
cursor = connection.cursor()

cursor.execute(
    """
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    """
)

tables = [row[0] for row in cursor.fetchall()]
print("Existing tables:", tables)

cursor.close()
connection.close()
