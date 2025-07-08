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
        user = auth.create_user(
            email=email, 
            password=password,
            display_name=full_name
        )
        
        # Store user info in session for this demo
        # In production, you'd want to use a proper database
        session[f'user_data_{user.uid}'] = {
            "uid": user.uid,
            "email": email,
            "role": role,
            "fullName": full_name,
            "company": data.get('company'),
            "matricNumber": data.get('matricNumber'),
            "school": data.get('school'),
            "programme": data.get('programme'),
            "level": data.get('level'),
            "courses": data.get('courses', [])
        }
        
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

        # Get user info from Firebase Auth
        user_record = auth.get_user(uid)
        
        # Store user info in session
        session['user_uid'] = uid
        session['user_email'] = user_record.email
        session['user_display_name'] = user_record.display_name or user_record.email
        
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
    user_uid = session.get('user_uid')
    
    # Try to get stored user data from session first
    user_data = session.get(f'user_data_{user_uid}')
    
    if user_data:
        return jsonify(user_data)
    else:
        # Fallback to basic info from Firebase Auth
        try:
            user_record = auth.get_user(user_uid)
            return jsonify({
                "uid": user_uid,
                "email": user_record.email,
                "fullName": user_record.display_name or user_record.email,
                "role": "intern"  # Default role since we don't have database
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/clock_in', methods=['POST'])
@login_required
def clock_in():
    user_uid = session['user_uid']
    now = datetime.now(TIMEZONE)
    today_str = now.strftime('%Y-%m-%d')
    
    # Check if already clocked in today (using session storage)
    clock_in_key = f'clock_in_{user_uid}_{today_str}'
    if session.get(clock_in_key):
        return jsonify({"success": False, "message": "You have already clocked in today."}), 409

    # Determine if late (after 9:00 AM)
    is_late = now.time() > datetime.strptime("09:00:00", "%H:%M:%S").time()

    # Store clock-in record in session
    session[clock_in_key] = {
        'user_uid': user_uid,
        'date': today_str,
        'clock_in_time': now.isoformat(),
        'is_late': is_late
    }

    return jsonify({
        "success": True, 
        "message": "Clock-in successful!",
        "time": now.strftime('%I:%M:%S %p'),
        "is_late": is_late
    }), 201

@app.route('/api/dashboard_data')
@login_required
def get_dashboard_data():
    user_uid = session['user_uid']
    user_data = session.get(f'user_data_{user_uid}', {})
    role = user_data.get('role', 'intern')
    
    if role in ['intern', 'student']:
        # Get personal attendance records from session
        records = []
        for key, value in session.items():
            if key.startswith(f'clock_in_{user_uid}_'):
                records.append(value)
        
        # Sort by date (newest first)
        records.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify({"records": records[:10]})  # Return last 10 records
    
    elif role == 'supervisor':
        # Get all clock-in records for today
        today_str = datetime.now(TIMEZONE).strftime('%Y-%m-%d')
        present_today = []
        
        for key, value in session.items():
            if key.startswith('clock_in_') and key.endswith(f'_{today_str}'):
                # Get user data for this record
                record_uid = value['user_uid']
                user_info = session.get(f'user_data_{record_uid}', {})
                
                if user_info.get('role') in ['intern', 'student']:
                    present_today.append({
                        **value,
                        'fullName': user_info.get('fullName', 'Unknown User')
                    })
        
        # Count total interns/students (mock data for demo)
        total_count = 5  # You can adjust this or calculate from actual data
        
        return jsonify({
            "present": present_today,
            "all_interns_count": total_count
        })
    
    return jsonify({"message": "Dashboard data is not available for this role."}), 501

if __name__ == '__main__':
    app.run(debug=True, port=5001)