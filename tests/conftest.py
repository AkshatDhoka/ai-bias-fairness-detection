import pytest
from backend.app import create_app
from backend.config import TestConfig
from backend.database.db import db
from backend.database.models import User

@pytest.fixture
def app():
    """Create Flask application instance in testing configuration."""
    app = create_app(config_class=TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Flask test client for issuing API requests."""
    return app.test_client()

@pytest.fixture
def registered_user(app):
    """Fixture providing a registered test user."""
    with app.app_context():
        user = User(
            name="Akshat Dhoka",
            email="akshat@example.com",
            role="USER"
        )
        user.set_password("SecurePassword123")
        db.session.add(user)
        db.session.commit()
        return user
