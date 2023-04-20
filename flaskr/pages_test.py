from flaskr import create_app
from flaskr.backend import Backend
import pytest, tempfile
import unittest
from unittest.mock import mock_open, patch

# See https://flask.palletsprojects.com/en/2.2.x/testing/
# for more info on testing


# creates a mock app fixture
@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
    })
    return app


# creates a mock client fixture
@pytest.fixture
def client(app):
    return app.test_client()


# creates a mock backend fixture
@pytest.fixture(scope="module")
def backend():
    return Backend()


def test_home_page(client):
    '''
    Testing that the homepage renders right when no one is logged-in
    '''
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Welcome to The Little Niche Recomendations Wiki!" in resp.data
    assert b"Explore all the great restaurants and eateries in the world, as recommended by locals!" in resp.data
    assert b"Little Niche Recomendations" in resp.data
    assert b"Home" in resp.data
    assert b"Pages" in resp.data
    assert b"About" in resp.data
    assert b"Upload" not in resp.data
    assert b"Logout" not in resp.data
    assert b"Login" in resp.data
    assert b"Sign Up" in resp.data

# tests that authentic renders main template & error
def test_signup_route(client):
    '''
    test /signup route redirects to signup.html
    '''
    resp = client.get("/signup")
    assert b"<h1>Sign Up</h1>" in resp.data


def test_signup_redirects(client):
    '''
    test that signup form redirects to /authenticate_new_user on submit
    '''
    username = "newestuser"
    password = "password12"
    resp = client.post("/authenticate_new_user",
                       data={
                           "username": username,
                           "password": password
                       })
    assert resp.status_code == 200


def test_authenticate_new_user_route(client):
    ''' 
    Mock the Backend and get authenticate_new_user method into variable mock_authentication
    set the return to expected return and then call the client. assert that the resp properly routed
    '''
    with patch("flaskr.backend.Backend.authenticate_new_user"
              ) as mock_authentication:
        mock_result = {'success': True, 'message': 'New Account Created!'}
        mock_authentication.return_value = mock_result
        username = "newestuser"
        password = "password12"
        resp = client.post("/authenticate_new_user",
                           data={
                               "username": username,
                               "password": password
                           })
        assert b"<title>Little Niche Recomendations</title>" in resp.data


def test_authenticate_new_user_route_incorrect(client):
    '''
    Mock the Backend and get authenticate_new_user method into variable mock_authentication
    set the return to expected return and then call the client. assert that the resp properly routed
    '''
    with patch("flaskr.backend.Backend.authenticate_new_user"
              ) as mock_authentication:
        mock_result = {
            'success':
                False,
            'message':
                'Username needs to be longer than four characters! Try again please.'
        }
        mock_authentication.return_value = mock_result
        username = "newestuser"
        password = "password1"
        resp = client.post("/authenticate_new_user",
                           data={
                               "username": username,
                               "password": password
                           })
        assert b"<h1>Sign Up</h1>" in resp.data


def test_authenticate_new_user_route_incorrect1(client):
    '''
    Mock the Backend and get authenticate_new_user method into variable mock_authentication
    set the return to expected return and then call the client. assert that the resp properly routed
    '''
    with patch("flaskr.backend.Backend.authenticate_new_user"
              ) as mock_authentication:
        mock_result = {
            'success':
                False,
            'message':
                'Password needs to include at least one number and be longer than 5 characters.'
        }
        mock_authentication.return_value = mock_result
        username = "newestuser"
        password = "password1"
        resp = client.post("/authenticate_new_user",
                           data={
                               "username": username,
                               "password": password
                           })
        assert b"<h1>Sign Up</h1>" in resp.data


def test_login_route(client):
    '''
    test /login route redirects to login.html
    '''
    resp = client.get("/login")
    assert b"<h1>Login</h1>" in resp.data


def test_login_redirects(client):
    '''
    test that /authenticate is routed to from login form
    '''
    username = "returningUser"
    password = "password12"
    resp = client.post("/authenticate",
                       data={
                           "username": username,
                           "password": password
                       })
    assert resp.status_code == 200


def test_authenticate_route(client):
    '''
    Mock the Backend and get authenticate_user method into variable mock_authentication
    set the return to expected return and then call the client. assert that the resp properly routed
    '''
    with patch(
            "flaskr.backend.Backend.authenticate_user") as mock_authentication:
        mock_result = {'success': True, 'message': 'Authentication successful.'}
        mock_authentication.return_value = mock_result
        username = "returningUser"
        password = "password12"
        resp = client.post("/authenticate",
                           data={
                               "username": username,
                               "password": password
                           })
        assert b"<title>Little Niche Recomendations</title>" in resp.data


def test_authenticate_route_incorrect(client):
    '''
    Mock the Backend and get authenticate_user method into variable mock_authentication
    set the return to expected return and then call the client. assert that the resp properly routed
    '''
    with patch(
            "flaskr.backend.Backend.authenticate_user") as mock_authentication:
        mock_result = {
            'success': False,
            'message': 'Invalid username or password.'
        }
        mock_authentication.return_value = mock_result
        username = "returningUser"
        password = "password1"
        resp = client.post("/authenticate",
                           data={
                               "username": username,
                               "password": password
                           })
        assert b"<h1>Login</h1>" in resp.data


def test_upload_route(client):
    '''
    test /upload route redirects to upload.html
    '''
    resp = client.get("/upload")
    assert b"<h1>Upload a doc to the Wiki</h1>" in resp.data


def test_upload_redirects(client):
    '''
    test that upload form redirects to /authenticate_upload on submit
    '''
    upload = "mock_upload_name"
    mock_file = tempfile.NamedTemporaryFile(delete=False)
    resp = client.post("/authenticate_upload",
                       data={
                           "upload": upload,
                           "file": mock_file
                       })
    assert resp.status_code == 200


def test_authenticate_upload_route(client):
    '''
    Mock the Backend and get authenticate_upload method into variable mock_authentication
    set the return to expected return and then call the client. assert that the resp properly routed
    '''
    with patch("flaskr.backend.Backend.authenticate_upload"
              ) as mock_authentication:
        mock_result = {
            'success': True,
            'message': 'File successfully uploaded!'
        }
        mock_authentication.return_value = mock_result
        upload = "file_name"
        mock_file = tempfile.NamedTemporaryFile(delete=False)
        resp = client.post("/authenticate_upload",
                           data={
                               "upload": upload,
                               "file": mock_file
                           })
        assert resp.status_code == 200
        assert b"<h1>Upload a doc to the Wiki</h1>" in resp.data


def test_authenticate_upload_route_incorrectName(client):
    '''
    Mock the Backend and get authenticate_upload method into variable mock_authentication
    set the return to expected return and then call the client. assert that the resp properly routed
    '''
    with patch("flaskr.backend.Backend.authenticate_upload"
              ) as mock_authentication:
        mock_result = {'success': False, 'message': 'Please enter a file name!'}
        mock_authentication.return_value = mock_result
        upload = "file_name"
        mock_file = tempfile.NamedTemporaryFile(delete=False)
        resp = client.post("/authenticate_upload",
                           data={
                               "upload": upload,
                               "file": mock_file
                           })
        assert resp.status_code == 200
        assert b"<h1>Upload a doc to the Wiki</h1>" in resp.data


def test_authenticate_upload_route_incorrectType(client):
    '''
    Mock the Backend and get authenticate_upload method into variable mock_authentication
    set the return to expected return and then call the client. assert that the resp properly routed
    '''
    with patch("flaskr.backend.Backend.authenticate_upload"
              ) as mock_authentication:
        mock_result = {
            'success': False,
            'message': 'You can only have .txt files'
        }
        mock_authentication.return_value = mock_result
        upload = "file_name"
        mock_file = tempfile.NamedTemporaryFile(delete=False)
        resp = client.post("/authenticate_upload",
                           data={
                               "upload": upload,
                               "file": mock_file
                           })
        assert resp.status_code == 200
        assert b"<h1>Upload a doc to the Wiki</h1>" in resp.data


def test_authenticate_upload_route_incorrectContents(client):
    '''
    Mock the Backend and get authenticate_upload method into variable mock_authentication
    set the return to expected return and then call the client. assert that the resp properly routed
    '''
    with patch("flaskr.backend.Backend.authenticate_upload"
              ) as mock_authentication:
        mock_result = {
            'success': False,
            'message': 'File is not in UTF-8 encoding!'
        }
        mock_authentication.return_value = mock_result
        upload = "file_name"
        mock_file = tempfile.NamedTemporaryFile(delete=False)
        resp = client.post("/authenticate_upload",
                           data={
                               "upload": upload,
                               "file": mock_file
                           })
        assert resp.status_code == 200
        assert b"<h1>Upload a doc to the Wiki</h1>" in resp.data


def test_authenticate_upload_route_EmptyFile(client):
    '''
    Mock the Backend and get authenticate_upload method into variable mock_authentication
    set the return to expected return and then call the client. assert that the resp properly routed
    '''
    with patch("flaskr.backend.Backend.authenticate_upload"
              ) as mock_authentication:
        mock_result = {'success': False, 'message': 'File is empty!'}
        mock_authentication.return_value = mock_result
        upload = "file_name"
        mock_file = tempfile.NamedTemporaryFile(delete=False)
        resp = client.post("/authenticate_upload",
                           data={
                               "upload": upload,
                               "file": mock_file
                           })
        assert resp.status_code == 200
        assert b"<h1>Upload a doc to the Wiki</h1>" in resp.data

def test_search_redirects(client):
    '''
    test that /search is routed to from search form
    '''
    searched = "search"
    resp = client.post("/search",
                       data={
                           "searched": searched
                       })
    assert resp.status_code == 200

def test_search_route(client):
    '''
    test /search route redirects to search.html
    '''
    searched = "search"
    resp = client.post("/search",
                       data={
                           "searched": searched
                       })
    assert resp.status_code == 200
    assert b"<title>Search</title>" in resp.data

def test_logout_route(client):
    '''
    test /logout route redirects to main.html
    '''
    resp = client.get("/logout")
    assert resp.status_code == 200
    assert b"<title>Little Niche Recomendations</title>" in resp.data


def test_about_page(client):
    '''
    Testing that the basic markup of about us page looks right
    '''
    resp = client.get("/about")
    assert resp.status_code == 200
    assert b"Home" in resp.data
    assert b"Pages" in resp.data
    assert b"About" in resp.data


def test_pages(client):
    '''
    Testing Basic make-up of pages, the actual list of pages will be tested in test_show_page
    '''
    resp = client.get("/pages")
    assert resp.status_code == 200
    assert b"Home" in resp.data
    assert b"Pages" in resp.data
    assert b"About" in resp.data


def test_show_page(client):
    '''
    Mock the Backend class and its get_wiki_page method
    '''
    with patch("flaskr.backend.Backend.get_wiki_page") as mock_get_wiki_page:
        mock_page = {"title": "Test Page", "content": "This is a test page."}
        mock_get_wiki_page.return_value = mock_page
        resp = client.get("/pages/1")
        assert resp.status_code == 200
        assert mock_page["title"].encode() in resp.data
        assert mock_page["content"].encode() in resp.data
        assert b"Home" in resp.data
        assert b"Pages" in resp.data
        assert b"About" in resp.data


def test_get_image(client):
    '''
    Mock the Backend class and its get_image method, this fully tests that the images for about us can be visible in the html
    '''
    with patch("flaskr.backend.Backend.get_image") as mock_get_image:
        mock_image_data = b"dummy image data"
        mock_get_image.return_value = mock_image_data
        resp = client.get("/image/test_image.jpg")
        assert resp.status_code == 200
        assert resp.data == mock_image_data
