from datetime import datetime, timezone
from backend.database.db import db
from backend.database.models import User, UserPreference
from backend.services.audit_service import log_event

class AuthService:
    """Service handling User registration, authentication, and session operations."""

    @staticmethod
    def register_user(name, email, password, role='USER', ip_address=None):
        """Register a new user with hashed password and default preferences."""
        email_clean = email.strip().lower()
        existing_user = User.query.filter_by(email=email_clean).first()
        if existing_user:
            return False, "An account with this email address already exists.", None

        new_user = User(
            name=name.strip(),
            email=email_clean,
            role=role.upper() if role in ['USER', 'ADMIN'] else 'USER'
        )
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.flush()  # Obtain new_user.userId

            # Create default UserPreference for the new user
            user_pref = UserPreference(
                userId=new_user.userId,
                theme='dark',
                notificationEmail=email_clean,
                language='en'
            )
            db.session.add(user_pref)
            db.session.commit()

            log_event(
                action='USER_REGISTERED',
                user_id=new_user.userId,
                details=f"User {new_user.email} registered successfully.",
                ip_address=ip_address
            )
            return True, "Registration successful.", new_user

        except Exception as e:
            db.session.rollback()
            return False, f"Registration failed due to a database error: {str(e)}", None

    @staticmethod
    def authenticate_user(email, password, ip_address=None):
        """Authenticate user credentials and update lastLogin timestamp."""
        email_clean = email.strip().lower()
        user = User.query.filter_by(email=email_clean).first()

        if not user or not user.check_password(password):
            log_event(
                action='LOGIN_FAILED',
                user_id=user.userId if user else None,
                details=f"Failed login attempt for email: {email_clean}",
                ip_address=ip_address
            )
            return False, "Invalid email or password.", None

        # Update last login timestamp
        user.lastLogin = datetime.now(timezone.utc)
        try:
            db.session.commit()
            log_event(
                action='USER_LOGGED_IN',
                user_id=user.userId,
                details=f"User {user.email} logged in successfully.",
                ip_address=ip_address
            )
            return True, "Login successful.", user
        except Exception as e:
            db.session.rollback()
            return False, f"Login error: {str(e)}", None

    @staticmethod
    def get_user_by_id(user_id):
        """Fetch user by primary key ID."""
        return db.session.get(User, user_id)

