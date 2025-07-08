# --- START OF CORRECTED app.py ---

import os
import pytz
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import firebase_admin
# IMPORTANT: Re-add firestore to use the database
from firebase_admin import credentials, auth, firestore
from dotenv import load_dotenv

load_dotenv()

# --- App & Firebase Initialization ---
app = Flask(__name__)
app.secret_key = os.urandom(24) # Secret key for session management

# Initialize Firebase Admin SDK
cred = credentials.Certificate("firebase-service-account.json")
firebase_admin.initialize_app(cred)

# IMPORTANT: Re-initialize the database client
db = firestore.client()

TIMEZONE = pytz.timezone('Africa/Lagos') # IMPORTANT: Set your company's timezone

# --- Decorator for protected routes ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_uid" not in session:
            return redirect(url_for('login_page'))
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
    try:
        email = data['email']
        password = data['password']
        role = data['role']
        full_name = data['fullName']

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
                'courses': data.get('courses', [])
            })

        # Save the user data to the Firestore database
        db.collection('users').document(user.uid).set(user_data)
        
        return jsonify({"success": True, "message": "User created successfully."}), 201
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    id_token = data.get('idToken') # Expecting ID token from frontend

    if not id_token:
        return jsonify({"success": False, "message": "ID token is required"}), 400

    try:
        # Verify the ID token using Firebase Admin SDK. This is secure.
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        
        # Get user data from Firestore to store in the session
        user_doc = db.collection('users').document(uid).get()
        if user_doc.exists:
            session['user_uid'] = uid
            session['user_info'] = user_doc.to_dict() # Store full user profile
            return jsonify({"success": True, "message": "Login successful"})
        else:
            return jsonify({"success": False, "message": "User data not found in database."}), 404
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Authentication error: {e}"}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True})

@app.route('/api/session_data')
@login_required
def get_session_data():
    return jsonify(session.get('user_info', {}))

@app.route('/api/clock_in', methods=['POST'])
@login_required
def clock_in():
    user_uid = session['user_uid']
    now = datetime.now(TIMEZONE)
    today_str = now.strftime('%Y-%m-%d')
    
    # Check if already clocked in today
    attendance_ref = db.collection('attendance')
    query = attendance_ref.where('user_uid', '==', user_uid).where('date', '==', today_str).limit(1)
    
    # Check if user already clocked in today
    existing_records = list(query.stream())
    if len(existing_records) > 0:
        return jsonify({"success": False, "message": "You have already clocked in today."}), 409

    # Determine if late (after 9:00 AM)
    is_late = now.time() > datetime.strptime("09:00:00", "%H:%M:%S").time()

    record = {
        'user_uid': user_uid,
        'fullName': session['user_info']['fullName'],
        'company': session['user_info'].get('company', ''), # For supervisor filtering
        'school': session['user_info'].get('school', ''), # For student filtering
        'date': today_str,
        'clock_in_time': now.isoformat(),
        'is_late': is_late
    }
    # Add the record to Firestore
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
    user_info = session['user_info']
    role = user_info['role']
    today_str = datetime.now(TIMEZONE).strftime('%Y-%m-%d')
    
    if role == 'intern' or role == 'student':
        query = db.collection('attendance').where('user_uid', '==', user_info['uid']).order_by('date', direction=firestore.Query.DESCENDING).limit(30)
        records = [doc.to_dict() for doc in query.stream()]
        return jsonify({"type": "personal", "records": records})

    elif role == 'supervisor':
        company = user_info['company']
        # Get today's attendance for this company
        attendance_query = db.collection('attendance').where('date', '==', today_str)
        all_attendance = [doc.to_dict() for doc in attendance_query.stream()]
        present_interns = [rec for rec in all_attendance if rec.get('company') == company]

        # Get all interns in this company
        users_query = db.collection('users').where('role', '==', 'intern')
        all_users = [doc.to_dict() for doc in users_query.stream()]
        all_interns = [user for user in all_users if user.get('company') == company]

        return jsonify({
            "type": "management",
            "present": present_interns,
            "all_interns_count": len(all_interns)
        })
    
    elif role == 'lecturer':
        school = user_info['school']
        # Get today's attendance for this school
        attendance_query = db.collection('attendance').where('date', '==', today_str)
        all_attendance = [doc.to_dict() for doc in attendance_query.stream()]
        present_interns = [doc.to_dict() for doc in attendance_query.stream()]

        # Get all students in this school
        users_query = db.collection('users').where('role', '==', 'student')
        all_users = [doc.to_dict() for doc in users_query.stream()]
        all_students = [user for user in all_users if user.get('school') == school]

        return jsonify({
            "type": "management",
            "present": present_interns,
            "all_interns_count": len(all_students)
        })
    
    return jsonify({"message": "Role not supported for this data view yet."}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5001)

# --- END OF CORRECTED app.py ---