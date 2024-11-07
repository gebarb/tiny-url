import pytest
import uuid
from web import app


@pytest.fixture
def global_var():
    pytest.first_url = None
    pytest.second_url = None
    pytest.first_custom_url = None
    pytest.second_custom_url = None
    pytest.dupe_hash = None

@pytest.fixture(scope='module')
def test_client():
    # Set the Testing configuration prior to creating the Flask application
    flask_app = app
    flask_app.config.update({'TESTING': True})

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as c:
        # Establish an application context
        with flask_app.app_context():
            yield c
