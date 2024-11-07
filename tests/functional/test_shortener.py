import pytest
import uuid

pytest.dupe_hash = str(uuid.uuid4())[:8]


def test_create_random_url(test_client):
    response = test_client.post('/url', data={
        'dest_url': 'https://www.graysonebarb.com'
    })
    pytest.first_url = response.get_json().get('url').replace(
        test_client.application.config.get('BASE_DOMAIN'), '').strip('/')
    assert response.status_code == 200

    response = test_client.post('/url/create', json={
        'dest_url': 'https://wwww.yahoo.com'
    })
    pytest.second_url = response.get_json().get('url').replace(
        test_client.application.config.get('BASE_DOMAIN'), '').strip('/')
    assert response.status_code == 200


def test_create_custom_url(test_client):
    response = test_client.post('/url', data={
        'dest_url': 'https://www.google.com',
        'src_url': pytest.dupe_hash
    })
    pytest.first_custom_url = response.get_json().get('url').replace(
        test_client.application.config.get('BASE_DOMAIN'), '').strip('/')
    assert response.status_code == 200

    response = test_client.post('/url/create', json={
        'dest_url': 'https://www.adroit-tt.com/',
        'dest_url': f"adroit-{pytest.dupe_hash[:2]}"
    })
    pytest.second_custom_url = response.get_json().get('url').replace(
        test_client.application.config.get('BASE_DOMAIN'), '').strip('/')
    assert response.status_code == 200


def test_create_custom_url_error(test_client):
    response = test_client.post('/url', json={
        'dest_url': 'https://www.google.com',
        'src_url': pytest.dupe_hash
    })

    assert response.status_code == 400
    assert b'CONFLICT! Short URL already exists.' in response.data


def test_delete_url(test_client):
    response = test_client.delete(f"/url/{pytest.second_url}")

    assert response.status_code == 200
    assert response.get_json().get('success') is True


def test_get_url(test_client):
    response = test_client.get(f"/url/{pytest.first_url}")

    assert response.status_code == 200
    assert response.get_json().get('url', None)
    assert response.get_json().get('url', {}).get('url') == 'https://www.graysonebarb.com'


def test_get_invalid_url(test_client):
    response = test_client.get('/url/invalid')

    assert response.status_code == 400
    assert b'The requested Short URL was not found in the system.' in response.data

def test_get_deleted_url(test_client):
    response = test_client.get(f"/url/{pytest.second_url}")
    
    assert response.status_code == 400
    assert b'This Short URL was deleted' in response.data



def test_redirect(test_client):
    response = test_client.get(f"/{pytest.first_url}")

    assert response.status_code == 302
    assert response.headers.get('Location') == 'https://www.graysonebarb.com'


def test_invalid_redirect(test_client):
    response = test_client.get('/invalid')

    assert response.status_code == 404
    assert b'The requested Short URL was not found in the system.' in response.data

    response = test_client.get(f"/{pytest.second_url}")

    assert response.status_code == 404
    assert b'The requested Short URL was not found in the system.' in response.data

def test_statistics(test_client):
    response = test_client.get(f"/stats/{pytest.first_url}")

    assert response.status_code == 200
    assert response.get_json().get('statistics', None)
    assert response.get_json().get('statistics', {}).get(
        'hash_key') == pytest.first_url
    assert response.get_json().get('statistics', {}).get('num_clicks') > 0


def test_invalid_statistics(test_client):
    response = test_client.get('/stats/invalid')

    assert response.status_code == 400
    assert b'The requested Short URL was not found in the system.' in response.data

def test_deleted_statistics(test_client):
    response = test_client.get(f"/stats/{pytest.second_url}")

    assert response.status_code == 400
    assert b'This Short URL was deleted' in response.data



