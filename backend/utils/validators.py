import re

def validate_registration_payload(data):
    """Validate user registration payload."""
    if not isinstance(data, dict):
        return False, "Invalid JSON payload"
    
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not name:
        return False, "Name is required"
    
    if not email or not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
        return False, "Valid email address is required"
    
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    return True, None


def validate_login_payload(data):
    """Validate user login payload."""
    if not isinstance(data, dict):
        return False, "Invalid JSON payload"
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email:
        return False, "Email is required"
    if not password:
        return False, "Password is required"
    
    return True, None


def validate_analysis_input(text, language='en'):
    """Validate text input for bias analysis."""
    if not text or not isinstance(text, str):
        return False, "Text input is required and must be a string."
    
    stripped_text = text.strip()
    if len(stripped_text) < 10:
        return False, "Input text is too short. Minimum 10 characters required."
    
    if len(stripped_text) > 10000:
        return False, "Input text exceeds maximum allowed length of 10,000 characters."
    
    allowed_languages = ['en']
    if language not in allowed_languages:
        return False, f"Unsupported language '{language}'. Currently supported: {', '.join(allowed_languages)}."
    
    return True, None
