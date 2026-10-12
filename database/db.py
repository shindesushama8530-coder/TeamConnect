
import os
import psycopg2
from dotenv import load_dotenv

# Load local environment variables from .env
load_dotenv()


def get_connection():
    # Use Neon PostgreSQL when DATABASE_URL is configured
    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        connection = psycopg2.connect(database_url)

    else:
        # Use local PostgreSQL during development
        connection = psycopg2.connect(
            host="localhost",
            database="teamconnect_db",
            user="postgres",
            password=os.environ.get("LOCAL_DB_PASSWORD"),
            port="5432"
        )

    print("Connected database:", connection.info.dbname)
    return connection
