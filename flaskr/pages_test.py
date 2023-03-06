from flaskr import create_app
import pytest
import unittest
from unittest.mock import patch, Mock
from flaskr.backend import Backend

# See https://flask.palletsprojects.com/en/2.2.x/testing/ 
# for more info on testing
@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()

# TODO(Checkpoint (groups of 4 only) Requirement 4): Change test to
# match the changes made in the other Checkpoint Requirements. This does not apply to our group
def test_home_page(client):
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

# TODO(Project 1): Write tests for other routes.
def test_about_page(client):
    resp = client.get("/about")
    assert resp.status_code == 200
    assert b"Home" in resp.data
    assert b"Pages" in resp.data
    assert b"About" in resp.data

def test_pages(client):
    resp = client.get("/pages")
    assert resp.status_code == 200
    assert b"Home" in resp.data
    assert b"Pages" in resp.data
    assert b"About" in resp.data

def test_show_page(client):
    # Mock the Backend class and its get_wiki_page method
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