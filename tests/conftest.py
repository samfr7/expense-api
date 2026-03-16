import pytest
from app import create_app
from app.extensions import db
from app.models.user import User


@pytest.fixture
def app():
    """Create and configure a new app instance for each test. (Function Scope)"""
    app = create_app("testing")

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Creates a basic user for testing."""
    with app.app_context():
        user = User(
            username="testuser",
            email_id="test@example.com",
            monthly_budget=1000,
        )
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        # Detach the instance so tests can query it freshly
        db.session.expunge(user)
        return user


@pytest.fixture
def auth_headers(client, test_user):
    """Returns headers with a valid JWT for test_user."""
    response = client.post(
        "/auth/login",
        json={"email_id": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    token = response.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
