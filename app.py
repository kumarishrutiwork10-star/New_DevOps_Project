from flask import Flask, request
import pymysql
import time
import os

app = Flask(__name__)


def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "db"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "appuser"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "appdb"),
        cursorclass=pymysql.cursors.DictCursor
    )

def initialize_database():
    for attempt in range(10):
        try:
            connection = get_db_connection()

            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL
                    )
                """)

            connection.commit()
            connection.close()

            print("Database connected and users table is ready.")
            return

        except pymysql.MySQLError as error:
            print(f"Database connection attempt {attempt + 1}/10 failed: {error}")
            time.sleep(3)

    raise RuntimeError("Could not connect to the MySQL database.")


@app.route("/")
def home():
    return "Welcome to my page"


@app.route("/add-user")
def add_user():
    name = request.args.get("name")

    if not name:
        return "Please provide a name. Example: /add-user?name=Shruti", 400

    if len(name) > 100:
        return "Name must be 100 characters or fewer.", 400

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (name) VALUES (%s)",
                (name,)
            )

        connection.commit()
    finally:
        connection.close()

    return f"User {name} added successfully!"


@app.route("/users")
def list_users():
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name FROM users ORDER BY id")
            users = cursor.fetchall()
    finally:
        connection.close()

    return {"users": users}


if __name__ == "__main__":
    initialize_database()
    app.run(host="0.0.0.0", port=5000)
