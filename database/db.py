import psycopg2


def get_connection():

    connection = psycopg2.connect(
        host="localhost",
        database="teamconnect_db",
        user="postgres",
        password="root",
        port="5432"
    )

    print("Connected database:", connection.info.dbname)

    return connection