# ChronoTrack Setup Guide

## 🗄️ PostgreSQL Database Setup

### Option 1: Local PostgreSQL Installation

#### Windows:
1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Run the installer and follow the setup wizard
3. Remember the password you set for the `postgres` user
4. PostgreSQL will run on port 5432 by default

#### macOS:
```bash
# Using Homebrew
brew install postgresql
brew services start postgresql

# Create a database user
createuser -s postgres
```

#### Ubuntu/Linux:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Switch to postgres user and create database
sudo -u postgres psql
```

### Option 2: Cloud PostgreSQL (Recommended for Production)

#### Supabase (Free Tier Available):
1. Go to https://supabase.com
2. Create a new project
3. Get your database URL from Settings > Database
4. Use the connection string in your `.env` file

#### Railway (Simple Setup):
1. Go to https://railway.app
2. Create new project > Add PostgreSQL
3. Copy the connection details

#### Render (Free Tier):
1. Go to https://render.com
2. Create new PostgreSQL database
3. Copy connection string

## 📧 Email Configuration Options

### Option 1: Gmail (Easiest Setup)

1. **Enable 2-Factor Authentication:**
   - Go to your Google Account settings
   - Security > 2-Step Verification > Turn On

2. **Generate App Password:**
   - Go to Security > 2-Step Verification > App passwords
   - Select "Mail" and generate password
   - Copy the 16-character password

3. **Update .env file:**
   ```env
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-16-char-app-password
   ```

### Option 2: Outlook/Hotmail

```env
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@outlook.com
MAIL_PASSWORD=your-password
```

### Option 3: SendGrid (Professional)

1. Sign up at https://sendgrid.com
2. Create API key
3. Update configuration:

```env
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
```

## 🔧 Complete Setup Process

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables
Update your `.env` file with your actual credentials:

```env
# Database Configuration (Choose one option)

# Option A: Local PostgreSQL
DB_HOST=localhost
DB_NAME=attendance_db
DB_USER=postgres
DB_PASSWORD=your-postgres-password
DB_PORT=5432

# Option B: Supabase
DB_HOST=db.your-project.supabase.co
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-supabase-password
DB_PORT=5432

# Option C: Railway/Render (use full connection string)
DATABASE_URL=postgresql://username:password@host:port/database

# Email Configuration (Gmail example)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Security Keys (generate secure random keys)
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
SECRET_KEY=your-flask-secret-key-change-this-too

# App Configuration
BASE_URL=http://localhost:5001
```

### Step 3: Create Database and Tables
```bash
python init_db.py
```

### Step 4: Test Email Configuration
```bash
python test_email.py
```

### Step 5: Start Application
```bash
python app.py
```

## 🧪 Testing Your Setup

### Test Database Connection:
```python
from database import db
try:
    result = db.execute_one("SELECT version()")
    print("Database connected:", result)
except Exception as e:
    print("Database error:", e)
```

### Test Email Sending:
The system will automatically test email when you register a new user.

## 🔒 Security Recommendations

1. **Change Default Keys:**
   - Generate secure random keys for JWT_SECRET_KEY and SECRET_KEY
   - Never use default keys in production

2. **Database Security:**
   - Use strong passwords
   - Enable SSL connections for cloud databases
   - Regularly backup your database

3. **Email Security:**
   - Use app passwords, not regular passwords
   - Consider professional email services for production

## 🚨 Troubleshooting

### Database Issues:
- **Connection refused:** Check if PostgreSQL is running
- **Authentication failed:** Verify username/password
- **Database doesn't exist:** Run `init_db.py`

### Email Issues:
- **Authentication failed:** Check app password setup
- **Connection timeout:** Verify SMTP settings
- **Emails not sending:** Check spam folder

### Application Issues:
- **Import errors:** Run `pip install -r requirements.txt`
- **Port already in use:** Change port in `app.py`
- **Session errors:** Clear browser cookies

## 📞 Need Help?

If you encounter any issues:
1. Check the error messages in terminal
2. Verify all credentials in `.env` file
3. Test database and email connections separately
4. Check firewall settings for database connections

Your custom authentication system is now ready to use! 🎉