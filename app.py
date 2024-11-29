from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS to handle cross-origin requests
import psycopg2  # Import psycopg2 for PostgreSQL database interaction
import uuid  # For generating a simple token (UUID)

# Initialize Flask app and enable CORS
app = Flask(__name__)  # Create a Flask app instance
CORS(app)  # Enable Cross-Origin Resource Sharing (CORS) to allow requests from different origins

# Database connection function
def get_db_connection():
    """
    This function establishes a connection to the PostgreSQL database using psycopg2.
    It connects to the Neon hosted database and returns the connection object.
    """
    connection = psycopg2.connect(
        host="ep-nameless-queen-a53rjqqq.us-east-2.aws.neon.tech",  # Neon host for PostgreSQL
        database="neondb",                                         # Neon database name
        user="neondb_owner",                                        # Neon database username
        password="faAnkog7FQ8j",                                   # Neon database password
        sslmode="require"                                          # SSL mode required for secure connection
    )
    return connection

# Define the login route
@app.route('/login', methods=['POST'])
def login():
    """
    This function handles the POST request to the '/login' route. It expects a JSON payload
    containing a 'username' and 'password'. It checks these credentials against a database and
    returns a token if successful or an error message if not.
    """
    try:
        # Parse the incoming JSON data from the request body
        data = request.get_json()  # Retrieve JSON data from the POST request
        username = data.get('username')  # Get the 'username' field from the JSON
        password = data.get('password')  # Get the 'password' field from the JSON

        # Connect to the PostgreSQL database
        connection = get_db_connection()  # Call the function to establish DB connection
        cursor = connection.cursor()  # Create a cursor to interact with the database

        # Execute a query to check if the user exists in the 'users' table
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))  # Query to find the user by username
        user = cursor.fetchone()  # Fetch the first matching row from the database

        if user:
            # If a user is found, compare the entered password with the stored password
            stored_password = user[2]  # Assume the stored password is in the third column of the result
            if password == stored_password:  # Simple string comparison to validate the password
                # If the password matches, generate a simple token (UUID)
                token = str(uuid.uuid4())  # Generate a unique UUID as a token for this session
                return jsonify({"message": "Login successful!", "token": token}), 200  # Return success message with token
            else:
                return jsonify({"message": "Invalid credentials"}), 401  # Return error if the password is incorrect
        else:
            return jsonify({"message": "User not found"}), 404  # Return error if the user does not exist in the database

    except psycopg2.Error as e:
        # Handle any PostgreSQL-specific errors (e.g., connection issues or query failures)
        return jsonify({"message": f"Database error: {e}"}), 500  # Return a 500 Internal Server Error with the error message
    except Exception as e:
        # Handle any other unforeseen errors that may occur during execution
        return jsonify({"message": f"An error occurred: {e}"}), 500  # Return a general error message with status 500
    finally:
        # Close the database cursor and connection to free up resources
        if cursor:
            cursor.close()  # Close the cursor if it was created
        if connection:
            connection.close()  # Close the connection to the database

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # Start the Flask app with debugging enabled, accessible on localhost:5000
