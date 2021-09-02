from mock import patch
from app import app
import utils
import json

def test_index():
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    #setup
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200
        assert b"Congratulations" in response.data

@patch('utils._query_metadata')
def test_index_with_videos(mockquery):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response contains the file list
    """
    #setup
    ret_videos = [
        {"filename": "1.mp4", "height": 123, "width": 432, "fps": 10},
        {"filename": "2.mp4", "height": 423, "width": 21, "fps": 20}
    ]
    mockquery.return_value = ret_videos
    with app.test_client() as client:
        response = client.get('/')
        for ret_video in ret_videos:
            assert ret_video['filename'] in response.data.decode()

@patch('utils._query_metadata')
def test_list(mockquery):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/list' page is requested (GET)
    THEN check that valid JSON listing videos is returned
    """
    #setup
    ret_videos = [
        {"filename": "1.mp4", "height": 123, "width": 432, "fps": 10},
        {"filename": "2.mp4", "height": 423, "width": 21, "fps": 20}
    ]
    mockquery.return_value = ret_videos
    with app.test_client() as client:
        response = client.get('/list')
        for ret_video in ret_videos:
            assert ret_video in json.loads(response.data.decode())
            

def test_upload():
    """
    GIVEN a Flask application configured for testing
    WHEN the '/upload' page is requested (GET)
    THEN check that file is uploaded and the metdata set in the database
    """
    assert(False, "TODO")

@patch('utils._check_s3')
@patch('utils._check_database')
def test_healthcheck(mockdbcheck, mocks3check):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/health' page is requested (GET)
    THEN check that the healthcheck passes when database and s3 are available
    """
    mockdbcheck.return_value = True
    mocks3check.return_value = True
    with app.test_client() as client:
        response = client.get('/health')
        assert response.status_code == 200

@patch('utils._check_s3')
@patch('utils._check_database')
def test_healthcheck_bad_db(mockdbcheck, mocks3check):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/health' page is requested (GET)
    THEN check that the healthcheck fails when the database is unavailable
    """
    mockdbcheck.return_value = False
    mocks3check.return_value = True
    with app.test_client() as client:
        response = client.get('/health')
        assert response.status_code == 500

@patch('utils._check_s3')
@patch('utils._check_database')
def test_healthcheck_bad_s3(mockdbcheck, mocks3check):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/health' page is requested (GET)
    THEN check that the healthcheck fails when an s3 bucket is unavailable
    """
    mockdbcheck.return_value = True
    mocks3check.return_value = False
    with app.test_client() as client:
        response = client.get('/health')
        assert response.status_code == 500
