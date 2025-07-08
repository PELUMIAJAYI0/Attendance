import bcrypt
import jwt
import secrets
import string
from datetime import datetime, timedelta
from flask import current_app
from database import db

class AuthUtils:
    @staticmethod
    def hash_password(password):
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password, hashed):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def generate_token(user_id, expires_in_hours=24):
        """Generate JWT token"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def verify_token(token):
        """Verify JWT token and return user_id"""
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def generate_verification_code():
        """Generate random verification code"""
        return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    
    @staticmethod
    def generate_reset_token():
        """Generate secure reset token"""
        return secrets.token_urlsafe(32)

class UserManager:
    @staticmethod
    def create_user(email, password, role, full_name, **kwargs):
        """Create new user"""
        hashed_password = AuthUtils.hash_password(password)
        verification_code = AuthUtils.generate_verification_code()
        
        query = """
        INSERT INTO users (email, password_hash, role, full_name, company, school, 
                          programme, level, matric_number, verification_code, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        params = (
            email, hashed_password, role, full_name,
            kwargs.get('company'), kwargs.get('school'),
            kwargs.get('programme'), kwargs.get('level'),
            kwargs.get('matricNumber'), verification_code,
            datetime.utcnow()
        )
        
        result = db.execute_one(query, params)
        return result['id'], verification_code
    
    @staticmethod
    def get_user_by_email(email):
        """Get user by email"""
        query = "SELECT * FROM users WHERE email = %s"
        return db.execute_one(query, (email,))
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        query = "SELECT * FROM users WHERE id = %s"
        return db.execute_one(query, (user_id,))
    
    @staticmethod
    def verify_user_email(email, verification_code):
        """Verify user email with code"""
        query = """
        UPDATE users 
        SET email_verified = TRUE, verification_code = NULL 
        WHERE email = %s AND verification_code = %s
        RETURNING id
        """
        result = db.execute_one(query, (email, verification_code))
        return result is not None
    
    @staticmethod
    def create_password_reset_token(email):
        """Create password reset token"""
        reset_token = AuthUtils.generate_reset_token()
        expires_at = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
        
        query = """
        UPDATE users 
        SET reset_token = %s, reset_token_expires = %s 
        WHERE email = %s
        RETURNING id
        """
        result = db.execute_one(query, (reset_token, expires_at, email))
        return reset_token if result else None
    
    @staticmethod
    def reset_password(reset_token, new_password):
        """Reset password using token"""
        hashed_password = AuthUtils.hash_password(new_password)
        
        query = """
        UPDATE users 
        SET password_hash = %s, reset_token = NULL, reset_token_expires = NULL 
        WHERE reset_token = %s AND reset_token_expires > %s
        RETURNING id
        """
        result = db.execute_one(query, (hashed_password, reset_token, datetime.utcnow()))
        return result is not None