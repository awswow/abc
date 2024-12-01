import psycopg2
from psycopg2 import sql
import os

def save_user_data(user_data):
    """Save the user data to the database."""
    try:
        # Establish a connection to the PostgreSQL database
        with psycopg2.connect(
            dbname="postgres",  # Replace with your database name
            user="postgres",  # Replace with your username
            password="admin",  # Replace with your password
            host="localhost",  # Change if your database is hosted elsewhere
        ) as connection:
            # Use a cursor to interact with the database
            with connection.cursor() as cursor:
                # Insert query
                insert_query = sql.SQL("""
                    INSERT INTO users (gender, name, photo_path, city, bio)
                    VALUES (%s, %s, %s, %s, %s)
                """)

                # Ensure you're passing 'photo_filename', not 'photo_path'
                cursor.execute(insert_query, (
                    user_data['gender'], user_data['name'], user_data['photo_filename'],
                    user_data['city'], user_data['bio']
                ))

                # Commit the transaction to the database
                connection.commit()

        print("User data saved successfully.")
    except Exception as e:
        # In case of an error, print it
        print(f"Error saving user data: {e}")
