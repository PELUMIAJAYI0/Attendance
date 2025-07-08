# ChronoTrack - Custom Authentication System

A modern attendance tracking system with custom authentication, email verification, and PostgreSQL database.

## Features

✅ **Custom Authentication** - No external dependencies  
✅ **Email Verification** - Secure 6-digit verification codes  
✅ **Password Reset** - Secure token-based password reset  
✅ **PostgreSQL Database** - Robust and scalable  
✅ **Role-based Access** - Intern, Student, Supervisor, Lecturer  
✅ **Secure Sessions** - JWT tokens and bcrypt password hashing  
✅ **Email Notifications** - Beautiful HTML email templates  

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup PostgreSQL
Install PostgreSQL and create a database:
```sql
CREATE DATABASE attendance_db;
CREATE USER attendance_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE attendance_db TO attendance_user;
```

### 3. Configure Environment
Update `.env` file with your settings:
```env
# Database
DB_HOST=localhost
DB_NAME=attendance_db
DB_USER=attendance_user
DB_PASSWORD=your_password
DB_PORT=5432

# Email (Gmail example)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key
SECRET_KEY=your-flask-secret-key
```

### 4. Initialize Database
```bash
python init_db.py
```

### 5. Run Application
```bash
python app.py
```

Visit `http://localhost:5001`

## Email Setup (Gmail)

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. Use the generated password in `MAIL_PASSWORD`

## Database Schema

### Users Table
- `id` - Primary key
- `email` - Unique email address
- `password_hash` - Bcrypt hashed password
- `role` - User role (intern/student/supervisor/lecturer)
- `full_name` - User's full name
- `company/school` - Organization details
- `email_verified` - Email verification status
- `verification_code` - 6-digit verification code
- `reset_token` - Password reset token

### Attendance Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `date` - Attendance date
- `clock_in_time` - Clock-in timestamp
- `is_late` - Late status (after 9:00 AM)

## Security Features

- **Password Hashing**: Bcrypt with salt
- **JWT Tokens**: Secure session management
- **Email Verification**: Required for account activation
- **Password Reset**: Secure token-based reset
- **SQL Injection Protection**: Parameterized queries
- **Session Security**: Secure session handling

## API Endpoints

### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login
- `POST /api/logout` - User logout
- `POST /api/verify-email` - Email verification
- `POST /api/forgot-password` - Request password reset
- `POST /api/reset-password` - Reset password

### Application
- `GET /api/session_data` - Get user session data
- `POST /api/clock_in` - Clock in attendance
- `GET /api/dashboard_data` - Get dashboard data

## User Roles

### Intern/Student
- Clock in/out functionality
- View personal attendance history
- Email verification required

### Supervisor/Lecturer
- View team attendance
- Monitor punctuality
- Generate reports

## Development

### Project Structure
```
├── app.py              # Main Flask application
├── database.py         # Database connection and utilities
├── auth_utils.py       # Authentication utilities
├── email_service.py    # Email service
├── init_db.py         # Database initialization
├── templates/         # HTML templates
├── static/           # CSS and JavaScript
└── requirements.txt  # Python dependencies
```

### Adding New Features
1. Update database schema in `init_db.py`
2. Add API endpoints in `app.py`
3. Update frontend in `templates/` and `static/`

## Production Deployment

1. **Environment Variables**: Use production values
2. **Database**: Use managed PostgreSQL service
3. **Email**: Use professional email service
4. **Security**: Enable HTTPS, update secret keys
5. **Monitoring**: Add logging and monitoring

## Troubleshooting

### Database Connection Issues
- Check PostgreSQL is running
- Verify database credentials in `.env`
- Ensure database exists

### Email Issues
- Verify SMTP settings
- Check app password for Gmail
- Test email connectivity

### Authentication Issues
- Clear browser sessions
- Check JWT secret key
- Verify password hashing

## License

© 2024 ChronoTrack. All Rights Reserved.