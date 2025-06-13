"""
Main module for the basic Python project.
This file contains the core Flask application logic and route handlers.
"""
# Import required modules
from dotenv import load_dotenv  # Load environment variables from .env file
import os  # For operating system related operations
from flask import Flask, render_template, request, session, flash, redirect, url_for  # Flask framework components
import re  # For regular expressions

# Import custom helper functions
from common.helpers import get_port, get_debug  # Custom helper functions for configuration

# Initialize Flask application
app = Flask(__name__)  # Create a new Flask application instance
app.secret_key = 'secret-key'  # Required for session

def validate_email(email): #check if email is in email format
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return bool(re.match(pattern, email))

def validate_password(password): #check if password is in password format
    pattern = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$'
    return bool(re.match(pattern, password))

def is_username_unique(username, users): #check if username is unique
    return not any(user['username'] == username for user in users)

def get_users(username: str, password: str, first_name: str, last_name: str, email: str): #get users
    """
    Returns a list of users with their details.
    Creates a dictionary with user information and returns it in a list.
    """
    return [{
        "username": username,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "email": email
    }]

@app.route('/', methods=['GET', 'POST']) #route to main page
def index(): 
    """Handle the main page."""
    # Initialize users in session if it doesn't exist
    if 'users' not in session:
        session['users'] = []
    
    if request.method == 'POST':  # Check if request is POST
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        
        errors = []
        if not username:
            errors.append("Username is required")
        elif not is_username_unique(username, session['users']):
            errors.append("Username must be unique")
            
        if not validate_password(password):
            errors.append("Password must be at least 8 characters long and contain both letters and numbers")
            
        if not validate_email(email):
            errors.append("Invalid email format")
            
        if not first_name:
            errors.append("First name is required")
            
        if not last_name:
            errors.append("Last name is required")
        
        if errors:
            flash('\n'.join(errors), 'error')
        else:
            # Add new user to the list
            current_users = session['users']
            current_users.extend(get_users(username, password, first_name, last_name, email))
            session['users'] = current_users
            flash('User added successfully!', 'success')
    
    return render_template('index.html', users=session['users'])

@app.route('/delete/<username>', methods=['POST'])
def delete_user(username):
    if 'users' in session:
        # Create a new list without the user to delete
        updated_users = []
        for user in session['users']:
            if user['username'] != username:
                updated_users.append(user)
        session['users'] = updated_users
    return redirect(url_for('index'))

@app.route('/edit/<username>', methods=['POST'])
def edit_user(username):
    """Edit a user by username."""
    if 'users' not in session:
        return redirect(url_for('index'))
        
    # Find the user to edit
    user_to_edit = next((user for user in session['users'] if user['username'] == username), None)
    if not user_to_edit:
        flash('User not found', 'error')
        return redirect(url_for('index'))
    
    # Get form data
    password = request.form.get('password', '')
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    email = request.form.get('email', '').strip()
    
    print(f"Received form data: password={password}, first_name={first_name}, last_name={last_name}, email={email}")  # Debug print
    
    # Validate input
    errors = []
    if not validate_password(password):
        errors.append("Password must be at least 8 characters long and contain both letters and numbers")
        
    if not validate_email(email):
        errors.append("Invalid email format")
        
    if not first_name:
        errors.append("First name is required")
        
    if not last_name:
        errors.append("Last name is required")
    
    if errors:
        flash('\n'.join(errors), 'error')
        return redirect(url_for('index'))
    
    # Update user
    for user in session['users']:
        if user['username'] == username:
            user['password'] = password
            user['first_name'] = first_name
            user['last_name'] = last_name
            user['email'] = email
            session.modified = True  # Ensure session is marked as modified
            print(f"Updated user data: {user}")  # Debug print
            break
    
    flash('User updated successfully!', 'success')
    return redirect(url_for('index'))

def main():
    """Main function that runs when the script is executed."""
    # Load environment variables
    load_dotenv()  # Load environment variables from .env file
    
    # Get configuration from environment variables
    port = get_port()  # Get port number from environment
    debug = get_debug()  # Get debug mode from environment
    
    # Run the Flask application
    app.run(host='0.0.0.0', port=port, debug=debug)  # Start Flask server with configuration

if __name__ == "__main__":
    main()  # Execute main function when script is run directly 