from flask_mail import Mail, Message
from flask import current_app, render_template_string
import os

mail = Mail()

class EmailService:
    @staticmethod
    def send_verification_email(email, full_name, verification_code):
        """Send email verification"""
        subject = "Verify Your ChronoTrack Account"
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(90deg, #22d3ee, #a78bfa); color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f9f9f9; }
                .code { font-size: 24px; font-weight: bold; color: #22d3ee; text-align: center; padding: 20px; background: white; border-radius: 8px; margin: 20px 0; }
                .footer { text-align: center; padding: 20px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to ChronoTrack!</h1>
                </div>
                <div class="content">
                    <h2>Hi {{ full_name }},</h2>
                    <p>Thank you for signing up for ChronoTrack. To complete your registration, please verify your email address using the code below:</p>
                    <div class="code">{{ verification_code }}</div>
                    <p>This code will expire in 24 hours. If you didn't create this account, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>© 2024 ChronoTrack. All Rights Reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        html_body = render_template_string(html_template, 
                                         full_name=full_name, 
                                         verification_code=verification_code)
        
        msg = Message(
            subject=subject,
            recipients=[email],
            html=html_body,
            sender=current_app.config['MAIL_USERNAME']
        )
        
        try:
            mail.send(msg)
            return True
        except Exception as e:
            print(f"Error sending verification email: {e}")
            return False
    
    @staticmethod
    def send_password_reset_email(email, full_name, reset_token):
        """Send password reset email"""
        subject = "Reset Your ChronoTrack Password"
        reset_url = f"{current_app.config.get('BASE_URL', 'http://localhost:5001')}/reset-password?token={reset_token}"
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(90deg, #22d3ee, #a78bfa); color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f9f9f9; }
                .button { display: inline-block; padding: 12px 24px; background: #22d3ee; color: white; text-decoration: none; border-radius: 8px; margin: 20px 0; }
                .footer { text-align: center; padding: 20px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset Request</h1>
                </div>
                <div class="content">
                    <h2>Hi {{ full_name }},</h2>
                    <p>You requested to reset your password for your ChronoTrack account. Click the button below to reset your password:</p>
                    <div style="text-align: center;">
                        <a href="{{ reset_url }}" class="button">Reset Password</a>
                    </div>
                    <p>This link will expire in 1 hour. If you didn't request this reset, please ignore this email.</p>
                    <p>If the button doesn't work, copy and paste this link: {{ reset_url }}</p>
                </div>
                <div class="footer">
                    <p>© 2024 ChronoTrack. All Rights Reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        html_body = render_template_string(html_template, 
                                         full_name=full_name, 
                                         reset_url=reset_url)
        
        msg = Message(
            subject=subject,
            recipients=[email],
            html=html_body,
            sender=current_app.config['MAIL_USERNAME']
        )
        
        try:
            mail.send(msg)
            return True
        except Exception as e:
            print(f"Error sending password reset email: {e}")
            return False