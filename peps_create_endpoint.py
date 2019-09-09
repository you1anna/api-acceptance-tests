import pytest
from framework.apiclient import ApiClient


@pytest.fixture
def given_a_peps_read_endpoint():
    url = "http://ec2-34-251-162-89.eu-west-1.compute.amazonaws.com/peps"
    headers = {'content-type': 'application/json'}
    session = ApiClient(url)
    yield url, headers, session


def test_when_peps_data_added(given_a_peps_read_endpoint):
    url, headers, session = given_a_peps_read_endpoint

    r = session.post(data=session.data('valid'), headers=headers)

    assert r.status_code == 201
    assert len(r.json()['id']) == 24
    assert r.json()['message'] == 'Entity created successfully!'
    assert r.json()['ok'] is True


def test_when_invalid_peps_data_added(given_a_peps_read_endpoint):
    url, headers, session = given_a_peps_read_endpoint

    r = session.post(data=session.data('invalid'), headers=headers)

    assert r.status_code == 400
    assert len(r.json()['id']) == 24
    assert r.json()['message'] == 'Entity created successfully!'
    assert r.json()['ok'] is True


def test_when_missing_param_added(given_a_peps_read_endpoint):
    url, headers, session = given_a_peps_read_endpoint

    r = session.post(data=session.data('missingparam'), headers=headers)

    assert r.status_code == 400
    assert r.json()['message'] == 'Invalid request - missing parameters'
    assert r.json()['ok'] is False
