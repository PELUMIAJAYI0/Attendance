#!/usr/bin/env python3
"""
Quick setup script for ChronoTrack
This will guide you through the entire setup process
"""

import os
import sys
import subprocess
import getpass
from dotenv import load_dotenv

def print_header(title):
    print("\n" + "="*50)
    print(f"🚀 {title}")
    print("="*50)

def print_step(step, description):
    print(f"\n📋 Step {step}: {description}")

def run_command(command, description):
    print(f"⚡ {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully!")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def setup_environment():
    print_header("ChronoTrack Quick Setup")
    print("This script will help you set up ChronoTrack with custom authentication.")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Install dependencies
    print_step(1, "Installing Python Dependencies")
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("💡 Try: pip3 install -r requirements.txt")
        if not run_command("pip3 install -r requirements.txt", "Installing with pip3"):
            return False
    
    # Database setup
    print_step(2, "Database Configuration")
    print("\n🗄️ Database Setup Options:")
    print("1. Local PostgreSQL (recommended for development)")
    print("2. Supabase (free cloud database)")
    print("3. Railway (simple cloud setup)")
    print("4. I'll configure manually")
    
    db_choice = input("\nChoose option (1-4): ").strip()
    
    if db_choice == "1":
        setup_local_postgres()
    elif db_choice == "2":
        setup_supabase()
    elif db_choice == "3":
        setup_railway()
    else:
        print("📝 Please manually update the database settings in .env file")
    
    # Email setup
    print_step(3, "Email Configuration")
    setup_email()
    
    # Initialize database
    print_step(4, "Database Initialization")
    if run_command("python init_db.py", "Creating database tables"):
        print("✅ Database tables created successfully!")
    else:
        print("❌ Database initialization failed. Check your database connection.")
        return False
    
    # Test configuration
    print_step(5, "Testing Configuration")
    print("🧪 Testing database connection...")
    run_command("python test_database.py", "Testing database")
    
    print("📧 Testing email configuration...")
    run_command("python test_email.py", "Testing email")
    
    # Final instructions
    print_header("Setup Complete! 🎉")
    print("✅ ChronoTrack is ready to use!")
    print("\n🚀 To start the application:")
    print("   python app.py")
    print("\n🌐 Then visit: http://localhost:5001")
    print("\n📚 For more help, check: setup_guide.md")
    
    return True

def setup_local_postgres():
    print("\n🐘 Local PostgreSQL Setup:")
    print("1. Install PostgreSQL from: https://www.postgresql.org/download/")
    print("2. Create a database named 'attendance_db'")
    print("3. Enter your PostgreSQL credentials below:")
    
    host = input("Database host (localhost): ").strip() or "localhost"
    port = input("Database port (5432): ").strip() or "5432"
    user = input("Database user (postgres): ").strip() or "postgres"
    password = getpass.getpass("Database password: ")
    
    update_env_file({
        'DB_HOST': host,
        'DB_PORT': port,
        'DB_USER': user,
        'DB_PASSWORD': password,
        'DB_NAME': 'attendance_db'
    })

def setup_supabase():
    print("\n☁️ Supabase Setup:")
    print("1. Go to https://supabase.com and create a project")
    print("2. Go to Settings > Database")
    print("3. Copy your connection details:")
    
    host = input("Supabase host (db.xxx.supabase.co): ").strip()
    password = getpass.getpass("Database password: ")
    
    update_env_file({
        'DB_HOST': host,
        'DB_PORT': '5432',
        'DB_USER': 'postgres',
        'DB_PASSWORD': password,
        'DB_NAME': 'postgres'
    })

def setup_railway():
    print("\n🚂 Railway Setup:")
    print("1. Go to https://railway.app")
    print("2. Create new project > Add PostgreSQL")
    print("3. Copy the connection string:")
    
    connection_string = input("Connection string: ").strip()
    
    update_env_file({
        'DATABASE_URL': connection_string
    })

def setup_email():
    print("\n📧 Email Setup Options:")
    print("1. Gmail (recommended)")
    print("2. Outlook")
    print("3. Custom SMTP")
    print("4. Skip (configure manually)")
    
    email_choice = input("\nChoose option (1-4): ").strip()
    
    if email_choice == "1":
        setup_gmail()
    elif email_choice == "2":
        setup_outlook()
    elif email_choice == "3":
        setup_custom_smtp()
    else:
        print("📝 Please manually update email settings in .env file")

def setup_gmail():
    print("\n📬 Gmail Setup:")
    print("1. Enable 2-Factor Authentication on your Google account")
    print("2. Go to Security > 2-Step Verification > App passwords")
    print("3. Generate an app password for 'Mail'")
    
    email = input("Gmail address: ").strip()
    app_password = getpass.getpass("App password (16 characters): ")
    
    update_env_file({
        'MAIL_SERVER': 'smtp.gmail.com',
        'MAIL_PORT': '587',
        'MAIL_USE_TLS': 'True',
        'MAIL_USERNAME': email,
        'MAIL_PASSWORD': app_password
    })

def setup_outlook():
    print("\n📮 Outlook Setup:")
    email = input("Outlook email: ").strip()
    password = getpass.getpass("Password: ")
    
    update_env_file({
        'MAIL_SERVER': 'smtp-mail.outlook.com',
        'MAIL_PORT': '587',
        'MAIL_USE_TLS': 'True',
        'MAIL_USERNAME': email,
        'MAIL_PASSWORD': password
    })

def setup_custom_smtp():
    print("\n⚙️ Custom SMTP Setup:")
    server = input("SMTP server: ").strip()
    port = input("SMTP port (587): ").strip() or "587"
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ")
    
    update_env_file({
        'MAIL_SERVER': server,
        'MAIL_PORT': port,
        'MAIL_USE_TLS': 'True',
        'MAIL_USERNAME': username,
        'MAIL_PASSWORD': password
    })

def update_env_file(updates):
    """Update .env file with new values"""
    env_path = '.env'
    
    # Read existing content
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()
    else:
        lines = []
    
    # Update or add new values
    updated_lines = []
    updated_keys = set()
    
    for line in lines:
        if '=' in line and not line.strip().startswith('#'):
            key = line.split('=')[0].strip()
            if key in updates:
                updated_lines.append(f"{key}={updates[key]}\n")
                updated_keys.add(key)
            else:
                updated_lines.append(line)
        else:
            updated_lines.append(line)
    
    # Add new keys that weren't in the file
    for key, value in updates.items():
        if key not in updated_keys:
            updated_lines.append(f"{key}={value}\n")
    
    # Write back to file
    with open(env_path, 'w') as f:
        f.writelines(updated_lines)
    
    print(f"✅ Updated .env file with new configuration")

if __name__ == "__main__":
    try:
        setup_environment()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")