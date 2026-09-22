import json
from backend.database.models import User, NLPModel

def test_health_check(client):
    """Verify health check endpoint returns 200 operational state."""
    res = client.get('/api/health')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['data']['status'] == 'healthy'


def test_database_initialization_and_model_seed(app):
    """Verify DB tables are created and NLP model metadata is seeded correctly."""
    with app.app_context():
        # Query seeded metadata
        model = NLPModel.query.filter_by(modelName='valhalla/distilbart-mnli-12-3').first()
        assert model is not None
        assert model.languageSupported == 'en'
        assert model.accuracy is None  # Ensures accuracy is NOT fake/hardcoded


def test_password_hashing(app):
    """Verify password hashing with Werkzeug produces non-plaintext hashes and verifies accurately."""
    with app.app_context():
        user = User(name="Lekha Simaria", email="lekha@example.com", role="USER")
        raw_password = "SecretPassword456"
        user.set_password(raw_password)

        # Assert password is NOT stored in plaintext
        assert user.passwordHash != raw_password
        assert user.passwordHash.startswith(('pbkdf2:sha256', 'scrypt'))

        # Assert check_password succeeds for correct password and fails for wrong password
        assert user.check_password(raw_password) is True
        assert user.check_password("WrongPassword") is False


def test_user_registration_success(client):
    """Verify successful user registration via REST API."""
    payload = {
        'name': 'Akshat Dhoka',
        'email': 'f028_akshat@college.edu',
        'password': 'StrongPassword123!'
    }
    res = client.post('/api/auth/register', json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data['success'] is True
    assert data['data']['user']['email'] == 'f028_akshat@college.edu'
    assert data['data']['user']['role'] == 'USER'


def test_user_registration_duplicate_email(client, registered_user):
    """Verify registration fails if email already exists."""
    payload = {
        'name': 'Duplicate User',
        'email': 'akshat@example.com',  # Existing fixture email
        'password': 'Password123'
    }
    res = client.post('/api/auth/register', json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert data['success'] is False
    assert "already exists" in data['message']


def test_user_login_success_and_session(client, registered_user):
    """Verify user authentication and session establishment."""
    payload = {
        'email': 'akshat@example.com',
        'password': 'SecurePassword123'
    }
    res = client.post('/api/auth/login', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['data']['user']['name'] == 'Akshat Dhoka'

    # Verify protected /api/auth/me session check
    me_res = client.get('/api/auth/me')
    assert me_res.status_code == 200
    me_data = me_res.get_json()
    assert me_data['data']['user']['email'] == 'akshat@example.com'


def test_user_login_invalid_credentials(client, registered_user):
    """Verify login failure with incorrect password."""
    payload = {
        'email': 'akshat@example.com',
        'password': 'WrongPassword999'
    }
    res = client.post('/api/auth/login', json=payload)
    assert res.status_code == 401
    data = res.get_json()
    assert data['success'] is False
    assert "Invalid email or password" in data['message']


def test_protected_route_unauthorized_access(client):
    """Verify protected endpoints reject unauthenticated requests with 401 status."""
    routes_to_test = [
        ('/api/auth/me', 'GET'),
        ('/api/analyze', 'POST'),
        ('/api/history', 'GET'),
        ('/api/reports', 'GET')
    ]
    for url, method in routes_to_test:
        if method == 'GET':
            res = client.get(url)
        else:
            res = client.post(url, json={'text': 'Sample input text testing'})
        assert res.status_code == 401, f"Failed 401 check for {url}"


def test_logout(client, registered_user):
    """Verify session termination upon logout."""
    # Login first
    client.post('/api/auth/login', json={'email': 'akshat@example.com', 'password': 'SecurePassword123'})
    
    # Confirm logged in
    assert client.get('/api/auth/me').status_code == 200

    # Logout
    logout_res = client.post('/api/auth/logout')
    assert logout_res.status_code == 200

    # Confirm session cleared
    assert client.get('/api/auth/me').status_code == 401
