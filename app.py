import os
import pytz
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_mail import Mail
from dotenv import load_dotenv

from database import db
from auth_utils import AuthUtils, UserManager
from email_service import EmailService, mail

load_dotenv()

# --- App Initialization ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')

# Email configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['BASE_URL'] = os.getenv('BASE_URL', 'http://localhost:5001')

# Initialize mail
mail.init_app(app)

TIMEZONE = pytz.timezone('Africa/Lagos')

# --- Decorators ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

def email_verified_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for('login_page'))
        
        user = UserManager.get_user_by_id(session['user_id'])
        if not user or not user['email_verified']:
            return redirect(url_for('verify_email_page'))
        return f(*args, **kwargs)
    return decorated_function

# --- Frontend Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/verify-email')
def verify_email_page():
    if "user_id" not in session:
        return redirect(url_for('login_page'))
    return render_template('verify_email.html')

@app.route('/reset-password')
def reset_password_page():
    token = request.args.get('token')
    if not token:
        return redirect(url_for('login_page'))
    return render_template('reset_password.html', token=token)

@app.route('/dashboard')
@login_required
@email_verified_required
def dashboard():
    return render_template('dashboard.html')

# --- API Routes ---
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data['email'].lower().strip()
        password = data['password']
        role = data['role']
        full_name = data['fullName']
        
        # Check if user already exists
        existing_user = UserManager.get_user_by_email(email)
        if existing_user:
            return jsonify({"success": False, "message": "Email already registered"}), 400
        
        # Validate password strength
        if len(password) < 6:
            return jsonify({"success": False, "message": "Password must be at least 6 characters"}), 400
        
        # Create user
        user_data = {
            'company': data.get('company'),
            'school': data.get('school'),
            'programme': data.get('programme'),
            'level': data.get('level'),
            'matricNumber': data.get('matricNumber')
        }
        
        user_id, verification_code = UserManager.create_user(
            email, password, role, full_name, **user_data
        )
        
        # Send verification email
        email_sent = EmailService.send_verification_email(email, full_name, verification_code)
        
        if email_sent:
            session['user_id'] = user_id
            return jsonify({
                "success": True, 
                "message": "Registration successful! Please check your email for verification code.",
                "requires_verification": True
            }), 201
        else:
            return jsonify({
                "success": True, 
                "message": "Registration successful! However, verification email could not be sent. Please contact support.",
                "requires_verification": True
            }), 201
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Registration failed: {str(e)}"}), 500

@app.route('/api/verify-email', methods=['POST'])
def verify_email():
    try:
        data = request.get_json()
        verification_code = data['code'].upper().strip()
        
        if "user_id" not in session:
            return jsonify({"success": False, "message": "Session expired"}), 401
        
        user = UserManager.get_user_by_id(session['user_id'])
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404
        
        if UserManager.verify_user_email(user['email'], verification_code):
            return jsonify({"success": True, "message": "Email verified successfully!"})
        else:
            return jsonify({"success": False, "message": "Invalid verification code"}), 400
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Verification failed: {str(e)}"}), 500

@app.route('/api/resend-verification', methods=['POST'])
def resend_verification():
    try:
        if "user_id" not in session:
            return jsonify({"success": False, "message": "Session expired"}), 401
        
        user = UserManager.get_user_by_id(session['user_id'])
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404
        
        if user['email_verified']:
            return jsonify({"success": False, "message": "Email already verified"}), 400
        
        # Generate new verification code
        verification_code = AuthUtils.generate_verification_code()
        query = "UPDATE users SET verification_code = %s WHERE id = %s"
        db.execute_query(query, (verification_code, user['id']))
        
        # Send email
        email_sent = EmailService.send_verification_email(
            user['email'], user['full_name'], verification_code
        )
        
        if email_sent:
            return jsonify({"success": True, "message": "Verification code sent!"})
        else:
            return jsonify({"success": False, "message": "Failed to send email"}), 500
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to resend: {str(e)}"}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data['email'].lower().strip()
        password = data['password']
        
        user = UserManager.get_user_by_email(email)
        if not user or not AuthUtils.verify_password(password, user['password_hash']):
            return jsonify({"success": False, "message": "Invalid email or password"}), 401
        
        session['user_id'] = user['id']
        
        if not user['email_verified']:
            return jsonify({
                "success": True, 
                "message": "Login successful, but email verification required",
                "requires_verification": True
            })
        
        return jsonify({"success": True, "message": "Login successful"})
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Login failed: {str(e)}"}), 500

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        email = data['email'].lower().strip()
        
        user = UserManager.get_user_by_email(email)
        if user:
            reset_token = UserManager.create_password_reset_token(email)
            if reset_token:
                EmailService.send_password_reset_email(
                    user['email'], user['full_name'], reset_token
                )
        
        # Always return success to prevent email enumeration
        return jsonify({
            "success": True, 
            "message": "If the email exists, a password reset link has been sent"
        })
        
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to process request"}), 500

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        reset_token = data['token']
        new_password = data['password']
        
        if len(new_password) < 6:
            return jsonify({"success": False, "message": "Password must be at least 6 characters"}), 400
        
        if UserManager.reset_password(reset_token, new_password):
            return jsonify({"success": True, "message": "Password reset successful"})
        else:
            return jsonify({"success": False, "message": "Invalid or expired reset token"}), 400
            
    except Exception as e:
        return jsonify({"success": False, "message": f"Reset failed: {str(e)}"}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True})

@app.route('/api/session_data')
@login_required
def get_session_data():
    user = UserManager.get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return jsonify({"error": "User not found"}), 404
    
    # Remove sensitive data
    user_data = dict(user)
    user_data.pop('password_hash', None)
    user_data.pop('verification_code', None)
    user_data.pop('reset_token', None)
    user_data.pop('reset_token_expires', None)
    
    return jsonify(user_data)

@app.route('/api/clock_in', methods=['POST'])
@login_required
@email_verified_required
def clock_in():
    try:
        user_id = session['user_id']
        now = datetime.now(TIMEZONE)
        today_str = now.strftime('%Y-%m-%d')
        
        # Check if already clocked in today
        query = "SELECT id FROM attendance WHERE user_id = %s AND date = %s"
        existing = db.execute_one(query, (user_id, today_str))
        
        if existing:
            return jsonify({"success": False, "message": "You have already clocked in today"}), 409
        
        # Determine if late (after 9:00 AM)
        is_late = now.time() > datetime.strptime("09:00:00", "%H:%M:%S").time()
        
        # Insert attendance record
        query = """
        INSERT INTO attendance (user_id, date, clock_in_time, is_late)
        VALUES (%s, %s, %s, %s)
        """
        db.execute_query(query, (user_id, today_str, now, is_late))
        
        return jsonify({
            "success": True,
            "message": "Clock-in successful!",
            "time": now.strftime('%I:%M:%S %p'),
            "is_late": is_late
        })
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Clock-in failed: {str(e)}"}), 500

@app.route('/api/dashboard_data')
@login_required
@email_verified_required
def get_dashboard_data():
    try:
        user = UserManager.get_user_by_id(session['user_id'])
        role = user['role']
        today_str = datetime.now(TIMEZONE).strftime('%Y-%m-%d')
        
        if role in ['intern', 'student']:
            # Get personal attendance records
            query = """
            SELECT date, clock_in_time, is_late 
            FROM attendance 
            WHERE user_id = %s 
            ORDER BY date DESC 
            LIMIT 30
            """
            records = db.execute_query(query, (user['id'],), fetch=True)
            return jsonify({"type": "personal", "records": records})
        
        elif role == 'supervisor':
            # Get company attendance data
            company = user['company']
            
            # Get today's attendance for company
            query = """
            SELECT u.full_name, a.clock_in_time, a.is_late
            FROM attendance a
            JOIN users u ON a.user_id = u.id
            WHERE a.date = %s AND u.company = %s AND u.role = 'intern'
            ORDER BY a.clock_in_time
            """
            present = db.execute_query(query, (today_str, company), fetch=True)
            
            # Get total intern count for company
            query = "SELECT COUNT(*) as count FROM users WHERE role = 'intern' AND company = %s"
            total_result = db.execute_one(query, (company,))
            total_count = total_result['count'] if total_result else 0
            
            return jsonify({
                "type": "management",
                "present": present,
                "all_interns_count": total_count
            })
        
        elif role == 'lecturer':
            # Get school attendance data
            school = user['school']
            
            # Get today's attendance for school
            query = """
            SELECT u.full_name, a.clock_in_time, a.is_late
            FROM attendance a
            JOIN users u ON a.user_id = u.id
            WHERE a.date = %s AND u.school = %s AND u.role = 'student'
            ORDER BY a.clock_in_time
            """
            present = db.execute_query(query, (today_str, school), fetch=True)
            
            # Get total student count for school
            query = "SELECT COUNT(*) as count FROM users WHERE role = 'student' AND school = %s"
            total_result = db.execute_one(query, (school,))
            total_count = total_result['count'] if total_result else 0
            
            return jsonify({
                "type": "management",
                "present": present,
                "all_interns_count": total_count
            })
        
        return jsonify({"message": "Role not supported"}), 400
        
    except Exception as e:
        return jsonify({"error": f"Failed to load dashboard data: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)