import os
import pytz
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import firebase_admin as fb_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv

load_dotenv()

# --- App & Firebase Initialization ---
app = Flask(__name__)
app.secret_key = os.urandom(24) # Secret key for session management

# Initialize Firebase Admin SDK
cred = credentials.Certificate("firebase-service-account.json")
fb_admin.initialize_app(cred)
TIMEZONE = pytz.timezone('Africa/Lagos') # IMPORTANT: Set your company's timezone

# --- Decorator for protected routes ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_uid" not in session:
            return redirect(url_for('login_page', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# --- Frontend Rendering Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# --- API Routes (for JavaScript) ---

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data['email']
    password = data['password']
    role = data['role']
    full_name = data['fullName']

    try:
        # Create user in Firebase Authentication
        user = auth.create_user(email=email, password=password)
        
        # Store additional user info in Firestore
        user_data = {
            "uid": user.uid,
            "email": email,
            "role": role,
            "fullName": full_name
        }
        # Add role-specific fields
        if role == 'intern' or role == 'supervisor':
            user_data['company'] = data['company']
        elif role == 'student':
            user_data.update({
                'matricNumber': data['matricNumber'],
                'school': data['school'],
                'programme': data['programme'],
                'level': data['level']
            })
        elif role == 'lecturer':
             user_data.update({
                'school': data['school'],
                'programme': data['programme'],
                'courses': data.get('courses', []) # List of course dicts
            })

        
        return jsonify({"success": True, "message": "User created successfully."}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    id_token = data.get('idToken') # Expecting ID token from frontend

    if not id_token:
        return jsonify({"success": False, "message": "ID token is required"}), 400

    try:
        # Verify the ID token using Firebase Admin SDK
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        # User is successfully authenticated via Firebase Auth
        session['user_uid'] = uid # Store UID in session to mark user as logged in
        return jsonify({"success": True, "message": "Authentication successful"})
    except Exception as e: # Catch any exceptions during token verification
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True})

@app.route('/api/session_data')
@login_required
def get_session_data():
    # With Firestore removed, we can only return basic info from the session
    # based on what was set during successful login
    user_uid = session.get('user_uid')
    return jsonify({"uid": user_uid}) # Return only the UID as we don't have more data without Firestore

@app.route('/api/clock_in', methods=['POST'])
@login_required
def clock_in():
    user_uid = session['user_uid']
    now = datetime.now(TIMEZONE)
    today_str = now.strftime('%Y-%m-%d')
    
    # Check if already clocked in today
    # NOTE: This check requires a database, which we've removed. This functionality is broken.
        return jsonify({"success": False, "message": "You have already clocked in today."}), 409

    # Determine if late (after 9:00 AM)
    is_late = now.time() > datetime.strptime("09:00:00", "%H:%M:%S").time()

    record = {
        'user_uid': user_uid,
        'date': today_str,
        'clock_in_time': now.isoformat(),
        'is_late': is_late # You might not be able to determine lateness without time data
    }
    db.collection('attendance').add(record)

    return jsonify({
        "success": True, 
        "message": "Clock-in successful!",
        "time": now.strftime('%I:%M:%S %p'),
        "is_late": is_late
    }), 201


@app.route('/api/dashboard_data')
@login_required
def get_dashboard_data():
    # With Firestore removed, dashboard data cannot be retrieved.
    # You will need to reimplement this using another database or method if needed.
    return jsonify({"message": "Dashboard data is not available without a database."}), 501 # 501 Not Implemented



if __name__ == '__main__':
    app.run(debug=True, port=5001)