import psycopg2
import logging
from datetime import datetime
from typing import List

# Function to connect to the PostgreSQL database
def get_db_connection():
    return psycopg2.connect(
        dbname="postgres",  # Replace with your database name
        user="postgres",  # Replace with your database user
        password="admin",  # Replace with your password
        host="localhost"  # Replace with your host if it's not local
    )

# Function to search for users based on gender, city, and age +-1
def search_for_users(gender: str, city: str, user_age: int) -> List[dict]:
    """Search users from the same city and +-1 age."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                min_age = user_age - 1
                max_age = user_age + 1
                cursor.execute("""
                    SELECT name, city, gender, age, photo_filename, bio
                    FROM users
                    WHERE city = %s AND age BETWEEN %s AND %s AND gender = %s
                """, (city, min_age, max_age, gender))

                users = cursor.fetchall()

                search_results = []
                for user in users:
                    user_data = {
                        "name": user[0],
                        "city": user[1],
                        "gender": user[2],
                        "age": user[3],
                        "photo_filename": user[4],
                        "bio": user[5]
                    }
                    search_results.append(user_data)

                return search_results

    except psycopg2.DatabaseError as e:
        logging.error(f"Database error: {e}")
        return []
    except Exception as e:
        logging.error(f"Unexpected error while searching for users: {e}")
        return []

# Function to format the results into a readable string for the bot
def format_search_results(users: List[dict]) -> str:
    """Formats the list of user data into a human-readable string."""
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

# Example usage
if __name__ == "__main__":
    gender = "Girl"  # Example gender
    city = "New York"  # Example city
    user_age = 25  # Example age

    # Call the search function
    users = search_for_users(gender, city, user_age)

    # Format the results for display
    formatted_results = format_search_results(users)
    print(formatted_results)
