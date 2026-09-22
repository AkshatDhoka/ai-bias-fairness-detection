from datetime import datetime, timezone
from backend.database.db import db
from backend.database.models import AuditLog

def log_event(action, user_id=None, details=None, ip_address=None):
    """Record audit log entry for system actions and security events."""
    try:
        log_entry = AuditLog(
            userId=user_id,
            action=action,
            details=details,
            ipAddress=ip_address,
            performedAt=datetime.now(timezone.utc)
        )
        db.session.add(log_entry)
        db.session.commit()
        return log_entry
    except Exception as e:
        db.session.rollback()
        # Log failure silently so audit logging does not crash primary operations
        print(f"[Audit Service Error]: Failed to write audit log: {str(e)}")
        return None

