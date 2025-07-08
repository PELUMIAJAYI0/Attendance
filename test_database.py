#!/usr/bin/env python3
"""
Database connection test script
Run this to verify your PostgreSQL connection works
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def test_database_connection():
    """Test database connection"""
    print("🧪 Testing Database Connection...")
    
    # Try to get connection details
    db_host = os.getenv('DB_HOST', 'localhost')
    db_name = os.getenv('DB_NAME', 'attendance_db')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD')
    db_port = os.getenv('DB_PORT', '5432')
    
    print(f"🏠 Host: {db_host}")
    print(f"🗄️ Database: {db_name}")
    print(f"👤 User: {db_user}")
    print(f"🔌 Port: {db_port}")
    print(f"🔑 Password: {'*' * len(db_password or '')}")
    
    if not db_password:
        print("❌ Error: DB_PASSWORD must be set in .env file")
        return False
    
    try:
        # Test connection
        conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port=db_port
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print(f"✅ Database connected successfully!")
        print(f"📊 PostgreSQL Version: {version[0]}")
        
        # Test if tables exist
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"📋 Existing tables: {[table[0] for table in tables]}")
        else:
            print("📋 No tables found. Run 'python init_db.py' to create tables.")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Database connection failed: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check if PostgreSQL is running")
        print("2. Verify database credentials in .env file")
        print("3. Ensure database exists (create it if needed)")
        print("4. Check firewall settings")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    test_database_connection()