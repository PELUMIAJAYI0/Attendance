#!/usr/bin/env python3
"""
Email configuration test script
Run this to verify your email settings work correctly
"""

import os
from flask import Flask
from flask_mail import Mail, Message
from dotenv import load_dotenv

load_dotenv()

# Create test Flask app
app = Flask(__name__)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

mail = Mail(app)

def test_email_config():
    """Test email configuration"""
    print("🧪 Testing Email Configuration...")
    print(f"📧 Mail Server: {app.config['MAIL_SERVER']}")
    print(f"🔌 Port: {app.config['MAIL_PORT']}")
    print(f"🔒 TLS: {app.config['MAIL_USE_TLS']}")
    print(f"👤 Username: {app.config['MAIL_USERNAME']}")
    print(f"🔑 Password: {'*' * len(app.config['MAIL_PASSWORD'] or '')}")
    
    if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
        print("❌ Error: MAIL_USERNAME and MAIL_PASSWORD must be set in .env file")
        return False
    
    try:
        with app.app_context():
            msg = Message(
                subject="ChronoTrack Email Test",
                recipients=[app.config['MAIL_USERNAME']],  # Send to yourself
                html="""
                <h2>🎉 Email Configuration Successful!</h2>
                <p>Your ChronoTrack email system is working correctly.</p>
                <p>You can now:</p>
                <ul>
                    <li>✅ Send verification emails</li>
                    <li>✅ Send password reset emails</li>
                    <li>✅ Notify users of important updates</li>
                </ul>
                <p><strong>Next step:</strong> Run your ChronoTrack application!</p>
                """,
                sender=app.config['MAIL_USERNAME']
            )
            
            mail.send(msg)
            print("✅ Test email sent successfully!")
            print(f"📬 Check your inbox: {app.config['MAIL_USERNAME']}")
            return True
            
    except Exception as e:
        print(f"❌ Email test failed: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check your email credentials in .env file")
        print("2. For Gmail: Enable 2FA and use App Password")
        print("3. Check if 'Less secure app access' is enabled (if not using App Password)")
        print("4. Verify SMTP server and port settings")
        return False

if __name__ == "__main__":
    test_email_config()