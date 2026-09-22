from flask import Blueprint, request, session
from backend.services.auth_service import AuthService
from backend.services.audit_service import log_event
from backend.utils.validators import validate_registration_payload, validate_login_payload
from backend.utils.helpers import api_response

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user account."""
    data = request.get_json(silent=True) or {}
    is_valid, err_msg = validate_registration_payload(data)
    if not is_valid:
        return api_response(success=False, message=err_msg, status_code=400)
    
    ip_addr = request.remote_addr
    success, message, user = AuthService.register_user(
        name=data['name'],
        email=data['email'],
        password=data['password'],
        role=data.get('role', 'USER'),
        ip_address=ip_addr
    )

    if not success:
        return api_response(success=False, message=message, status_code=400)
    
    return api_response(
        success=True, 
        message=message, 
        data={'user': user.to_dict()}, 
        status_code=201
    )


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user credentials and create session."""
    data = request.get_json(silent=True) or {}
    is_valid, err_msg = validate_login_payload(data)
    if not is_valid:
        return api_response(success=False, message=err_msg, status_code=400)

    ip_addr = request.remote_addr
    success, message, user = AuthService.authenticate_user(
        email=data['email'],
        password=data['password'],
        ip_address=ip_addr
    )

    if not success:
        return api_response(success=False, message=message, status_code=401)
    
    # Establish session
    session.clear()
    session['user_id'] = user.userId
    session['user_role'] = user.role
    session['user_name'] = user.name

    return api_response(
        success=True,
        message=message,
        data={'user': user.to_dict()},
        status_code=200
    )


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Log out current user and clear session."""
    user_id = session.get('user_id')
    if user_id:
        log_event(
            action='USER_LOGGED_OUT',
            user_id=user_id,
            details="User logged out.",
            ip_address=request.remote_addr
        )
    session.clear()
    return api_response(success=True, message="Successfully logged out.", status_code=200)


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Retrieve details of currently logged-in user session."""
    user_id = session.get('user_id')
    if not user_id:
        return api_response(success=False, message="Unauthorized. Please log in.", status_code=401)
    
    user = AuthService.get_user_by_id(user_id)
    if not user:
        session.clear()
        return api_response(success=False, message="User session invalid.", status_code=401)

    return api_response(
        success=True,
        message="Session active.",
        data={'user': user.to_dict()},
        status_code=200
    )
