import psycopg2
import psycopg2.extras
from decouple import config

def get_connection() -> psycopg2.extensions.connection:
    return psycopg2.connect(
        dbname=config("DB_NAME", default="railway_db"),
        user=config("DB_USER", default="railway"),
        password=config("DB_PASSWORD", default="railway"),
        host=config("DB_HOST", default="db"),
        port=config("DB_PORT", default="5432"),
    )
