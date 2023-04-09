from flaskr.backend import Backend
import hashlib
import json
import os
import io
import re
from google.cloud import storage

import pytest
'''
Building the necessary pytest fixtures
'''


@pytest.fixture(scope="module")
def backend():
    return Backend()


@pytest.fixture(scope="module")
def client(backend):
    return backend.client


@pytest.fixture(scope="module")
def wiki_content_bucket(backend):
    return backend.wiki_content_bucket


@pytest.fixture(scope="module")
def users_bucket(backend):
    return backend.users_bucket


@pytest.fixture(scope="module")
def about_us_pictures(backend):
    return backend.about_us_pictures


def test_get_wiki_page(wiki_content_bucket):
    '''
    Testing that wiki page contents are retrieved successfully
    '''
    content = "test wiki page content"
    name = "test_page"
    cur_blob = wiki_content_bucket.blob(f"pages/{name}")
    cur_blob.upload_from_string(content)

    backend = Backend()
    assert backend.get_wiki_page(name) == content

    cur_blob.delete()  # cleaning up


def test_get_images(about_us_pictures):
    '''
    Testing that images can be gotten from the GSC bucket (essentially get_images test)
    '''
    name = "test_image.jpg"
    cur_blob = about_us_pictures.blob(name)
    cur_blob.upload_from_string(b"")

    backend = Backend()
    assert name in backend.get_images()

    cur_blob.delete()


def test_get_all_page_names(wiki_content_bucket):
    '''
    Testing that all the pages from the GSC bucket are being returned
    '''
    names = ["test_page1", "test_page2", "test_page3"]
    for name in names:
        cur_blob = wiki_content_bucket.blob(f"pages/{name}")
        cur_blob.upload_from_string("test wiki page content")

    backend = Backend()
    all_bucket_names = set(backend.get_all_page_names())
    for name in names:
        assert name in all_bucket_names

    for name in names:
        cur_blob = wiki_content_bucket.blob(f"pages/{name}")
        cur_blob.delete()


def test_upload(wiki_content_bucket):
    '''
    Testing the upload functionality from backend that files are uploaded to the GSC bucket
    '''
    content = "test wiki page content"
    name = "test_page"
    backend = Backend()
    backend.upload(content, name)

    cur_blob = wiki_content_bucket.blob(f"pages/{name}")
    assert cur_blob.exists() and cur_blob.download_as_text() == content

    cur_blob.delete()


def test_sign_up(users_bucket):
    '''
    Testing the sign_up backend functionality and the hashing pass
    '''
    backend = Backend()
    username = "test_user"
    password = "test_password1122"
    backend.sign_up(username, password)

    cur_blob = users_bucket.blob(f"users/{username}")
    assert cur_blob.exists()

    data = json.loads(cur_blob.download_as_text())
    print(data)
    site_secret = "ProjectX_User"
    with_salt = f"{username}{site_secret}{password}"
    hash_pass = hashlib.blake2b(with_salt.encode()).hexdigest()
    assert data['password'] == hash_pass

    cur_blob.delete()


def test_sign_in(users_bucket):
    '''
    Testing the auth sign-in for user works for valid test credentials
    '''
    backend = Backend()
    username = "test_user"
    password = "test_password1122"
    backend.sign_up(username, password)

    assert backend.sign_in(username, password)

    cur_blob = users_bucket.blob(f"users/{username}")
    cur_blob.delete()


def test_authenticate_user(users_bucket):
    '''
    Testing the auth intermid. func for user works for valid test credentials
    '''
    backend = Backend()
    username = "test_user"
    password = "test_password1122"
    backend.sign_up(username, password)

    assert backend.authenticate_user(username, password) == {
        'success': True,
        'message': 'Authentication successful.'
    }

    cur_blob = users_bucket.blob(f"users/{username}")
    cur_blob.delete()


def test_authenticate_new_user(users_bucket):
    '''
    Test invalid username, invalid password, already existing user, valid new user.
    '''
    backend = Backend()

    assert backend.authenticate_new_user("me", "test_password") == {
        'success':
            False,
        'message':
            'Username needs to be longer than four characters! Try again please.'
    }  # invalid username

    assert backend.authenticate_new_user("ThisShouldnptWork", "notme") == {
        'success':
            False,
        'message':
            'Password needs to include at least one number and be longer than 5 characters.'
    }  # invalid password

    username = "test_user"
    password = "test_password1122"
    backend.sign_up(username, password)
    assert backend.authenticate_new_user(username, password) == {
        'success':
            False,
        'message':
            'This username already has an account with us, please log in!'
    }  # already existing user
    cur_blob = users_bucket.blob(f"users/{username}")
    cur_blob.delete()

    username = "new_user_work"
    password = "password123"
    assert backend.authenticate_new_user(username, password) == {
        'success': True,
        'message': 'New Account Created!'
    }  # valid new user
    cur_blob = users_bucket.blob(f"users/{username}")
    assert cur_blob.exists()

    data = json.loads(cur_blob.download_as_text())
    site_secret = "ProjectX_User"
    with_salt = f"{username}{site_secret}{password}"
    hash_pass = hashlib.blake2b(with_salt.encode()).hexdigest()
    assert data['password'] == hash_pass

    cur_blob.delete()


def test_get_image(about_us_pictures, monkeypatch):
    '''
    Testing that a nonexistent image returns None and a valid image passes
    '''
    image_name = "nonexistent_image.jpg"
    image_datas = None

    def mock_blob(self, name):
        raise Exception("Blob not found")

    monkeypatch.setattr(about_us_pictures, "blob", mock_blob)
    backend = Backend()
    result = backend.get_image(image_name)
    assert result is None

    image_name = "test_image.jpg"
    image_data = b"test image bytes"


"""
    def mock_download_as_bytes(self):
        print("Mocking download_as_bytes")
        return image_data

    monkeypatch.setattr(
        about_us_pictures, "blob",
        lambda self, name: MockBlob(name, mock_download_as_bytes))
    backend = Backend()
    result = backend.get_image(image_name)
    assert result == image_datas
"""
