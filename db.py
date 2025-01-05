import psycopg2
import logging
from psycopg2 import sql
from typing import Optional, Dict

# Database connection parameters
DB_NAME = "postgres"  # Replace with your database name
DB_USER = "postgres"  # Replace with your username
DB_PASSWORD = "admin"  # Replace with your password
DB_HOST = "localhost"  # Replace with your database host (localhost or an IP)

# Function to connect to the PostgreSQL database
def get_db_connection():
    """Establish a connection to the database."""
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST
    )

def user_exists(chat_id: int) -> bool:
    """Check if a user exists in the database by their chat_id."""
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 1
                    FROM users
                    WHERE chat_id = %s
                """, (chat_id,))
                result = cursor.fetchone()
        return result is not None
    except Exception as e:
        logging.error(f"Error checking if user exists: {e}")
        return False

def save_user_data(user_data: Dict[str, str]):
    """Save the user data to the database."""
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                insert_query = sql.SQL(""" 
                    INSERT INTO users (chat_id, gender, name, photo_filename, city, bio, age, username)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """)
                cursor.execute(insert_query, (
                    user_data['chat_id'],
                    user_data['gender'],
                    user_data['name'],
                    user_data['photo_filename'],
                    user_data.get('city', None),
                    user_data.get('bio', None),
                    user_data.get('age', None),
                    user_data.get('username', None)
                ))
            connection.commit()
        logging.info("User data saved successfully.")
    except Exception as e:
        logging.error(f"Error saving user data: {e}")

def find_user(chat_id: int) -> Optional[Dict[str, str]]:
    """Find a user in the database by their chat ID."""
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(""" 
                    SELECT chat_id, gender, name, photo_filename, city, bio, age, username
                    FROM users
                    WHERE chat_id = %s
                """, (chat_id,))
                result = cursor.fetchone()
        
        if result:
            return {
                "chat_id": result[0],
                "gender": result[1],
                "name": result[2],
                "photo_filename": result[3],
                "city": result[4],
                "bio": result[5],
                "age": result[6],
                "username": result[7],
            }
        else:
            return None
    except Exception as e:
        logging.error(f"Error occurred while finding user: {e}")
        return None

def update_user_profile(chat_id: int, updated_data: Dict[str, str]):
    """Update specific fields of a user's profile data."""
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                set_clause = []
                values = []

                for key, value in updated_data.items():
                    set_clause.append(sql.SQL("{} = %s").format(sql.Identifier(key)))
                    values.append(value)

                set_clause = sql.SQL(", ").join(set_clause)
                values.append(chat_id)  # Add chat_id as the last value for WHERE clause

                update_query = sql.SQL(""" 
                    UPDATE users 
                    SET {set_clause} 
                    WHERE chat_id = %s 
                """).format(set_clause=set_clause)

                cursor.execute(update_query, values)
            connection.commit()

        logging.info(f"User profile with chat_id {chat_id} updated successfully.")
    except Exception as e:
        logging.error(f"Error updating user profile: {e}")

def get_users_in_city_and_age(gender: str, city: str, min_age: int, max_age: int) -> list:
    """Find users in the same city and with an age range of +-1 year from the given age."""
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                query = """
                    SELECT name, city, gender, age, photo_filename, bio
                    FROM users
                    WHERE city = %s AND age BETWEEN %s AND %s AND gender = %s
                """
                cursor.execute(query, (city, min_age, max_age, gender))
                users = cursor.fetchall()

        user_list = []
        for user in users:
            user_data = {
                "name": user[0],
                "city": user[1],
                "gender": user[2],
                "age": user[3],
                "photo_filename": user[4],
                "bio": user[5]
            }
            user_list.append(user_data)

        return user_list
    except Exception as e:
        logging.error(f"Error fetching users for search: {e}")
        return []

def format_user_data(users) -> str:
    """Formats the list of users into a human-readable string."""
    if not users:
        return "No users found with the specified criteria."
    
    results = ""
    for user in users:
        results += f"Name: {user['name']}\n"
        results += f"City: {user['city']}\n"
        results += f"Gender: {user['gender']}\n"
        results += f"Age: {user['age']}\n"
        results += f"Bio: {user['bio']}\n\n"

    return results
