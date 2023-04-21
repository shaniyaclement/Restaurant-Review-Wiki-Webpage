from flaskr.backend import Backend
import hashlib
import json
import os
import io
import re
from google.cloud import storage
from unittest.mock import mock_open, patch, MagicMock

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
"""
def test_filter_search(wiki_content_bucket):
    '''
    Testing the functionality that the function properly returns only the list of names that match given search
    '''
    backend = Backend()
    names = ["test_page1", "test_page2", "page3"]
    for name in names:
        cur_blob = wiki_content_bucket.blob(f"pages/{name}")
        if name == "test_page1":
            cur_blob.upload_from_string("this is the most lovely steak i've had")
        if name == "test_page2":
            cur_blob.upload_from_string("i this steak is the best")
        if name == "page3":
            cur_blob.upload_from_string("test mmm love the burger. i staff was incredible")
        else:
            cur_blob.upload_from_string("test wiki page content")
    
    ''' 
    if the search has no word/ phrase it returns all pages
    '''
    result_pages = ["test_page1", "test_page2", "page3"]
    searched = ''
    output = set(backend.filter_search(searched))
    for page in result_pages:
        assert page in output

    ''' 
    if the search has a word that is in some page titles and some content,
    return match (in this case all) tests if checks both title and content
    '''
    searched = 'test'
    output = set(backend.filter_search(searched))
    for page in result_pages:
        assert page in output
   
    ''' 
    test if there is matches regardless of capitilization
    '''
    result_pages = ["test_page1", "test_page2"]
    searched = 'THIS'
    output = set(backend.filter_search(searched))
    for page in result_pages:
        assert page in output
    
    for name in names:
        cur_blob = wiki_content_bucket.blob(f"pages/{name}")
        cur_blob.delete()
"""
def _create_test_data(wiki_content_bucket):
    names = ["test_page1", "test_page2", "page3"]
    for name in names:
        cur_blob = wiki_content_bucket.blob(f"pages/{name}")
        if name == "test_page1":
            cur_blob.upload_from_string("this is the most lovely steak i've had")
        if name == "test_page2":
            cur_blob.upload_from_string("i this steak is the best")
        if name == "page3":
            cur_blob.upload_from_string("test mmm love the burger. i staff was incredible")
        else:
            cur_blob.upload_from_string("test wiki page content")
    return names

def _clean_up_test_data(wiki_content_bucket, names):
    for name in names:
        cur_blob = wiki_content_bucket.blob(f"pages/{name}")
        cur_blob.delete()

def test_filterSearch_emptySearch_returnsAllPages(wiki_content_bucket):
    backend = Backend()
    names = _create_test_data(wiki_content_bucket)

    searched = ''
    output = set(backend.filter_search(searched))

    for page in names:
        assert page in output

    _clean_up_test_data(wiki_content_bucket, names)

def test_filterSearch_searchInTitleAndContent_returnsMatchingPages(wiki_content_bucket):
    backend = Backend()
    names = _create_test_data(wiki_content_bucket)

    searched = 'test'
    output = set(backend.filter_search(searched))

    for page in names:
        assert page in output

    _clean_up_test_data(wiki_content_bucket, names)

def test_filterSearch_ignoreCase_returnsMatchingPages(wiki_content_bucket):
    backend = Backend()
    names = _create_test_data(wiki_content_bucket)

    result_pages = ["test_page1", "test_page2"]
    searched = 'THIS'
    output = set(backend.filter_search(searched))

    for page in result_pages:
        assert page in output

    _clean_up_test_data(wiki_content_bucket, names)


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
    image_data = None

    def mock_blob(self, name):
        raise Exception("Blob not found")

    monkeypatch.setattr(about_us_pictures, "blob", mock_blob)
    backend = Backend()
    result = backend.get_image(image_name)
    assert result is None

    image_name = "test_image.jpg"
    image_data = b"test image bytes"


def test_edit_page(wiki_content_bucket):
    '''
    Testing that a page can be edited successfully
    '''
    content = "original content"
    name = "test_page"
    username = "test_user"
    og_fn = name
    cur_blob = wiki_content_bucket.blob(f"pages/{name}")
    cur_blob.upload_from_string(content)

    new_content = "new content"
    new_name = "new_page"
    backend = Backend()
    backend.edit_page(new_content, new_name, username, og_fn)
    assert wiki_content_bucket.blob(f"pages/{new_name}").exists()

    wiki_content_bucket.blob(f"pages/{new_name}").delete()


def test_edit_page_with_same_name(wiki_content_bucket):
    '''
    Testing that a page can be edited with the same name successfully
    '''
    content = "original content"
    name = "test_page"
    username = "test_user"
    og_fn = name
    cur_blob = wiki_content_bucket.blob(f"pages/{name}")
    cur_blob.upload_from_string(content)

    new_content = "new content"
    backend = Backend()
    backend.edit_page(new_content, name, username, og_fn)
    assert wiki_content_bucket.blob(f"pages/{name}").exists()

    wiki_content_bucket.blob(f"pages/{name}").delete()


def test_authenticate_edit_invalid_file_type():
    '''
    Testing that a file with an invalid file type is not allowed to be uploaded
    '''
    backend = Backend()
    uploaded_file = io.BytesIO(b'test content')
    uploaded_file.filename = 'test_page.jpg'
    result = backend.authenticate_edit(uploaded_file, "test_page", "",
                                       "test_user")
    assert result['success'] == False
    assert result['message'] == 'You can only have .txt files'


def test_authenticate_edit_empty_file():
    '''
    Testing that an empty file is not allowed to be uploaded
    '''
    backend = Backend()
    uploaded_file = io.BytesIO(b'')
    uploaded_file.filename = 'test_page.txt'
    result = backend.authenticate_edit(uploaded_file, "test_page", "",
                                       "test_user")
    assert result['success'] == False
    assert result['message'] == 'File is empty!'


def test_authenticate_edit_invalid_encoding():
    '''
    Testing that a file with invalid encoding is not allowed to be uploaded
    '''
    backend = Backend()
    uploaded_file = io.BytesIO(b'\xa5\x90\x96\n')
    uploaded_file.filename = 'test_page.txt'
    result = backend.authenticate_edit(uploaded_file, "test_page", "",
                                       "test_user")
    assert result['success'] == False
    assert result['message'] == 'File is not in UTF-8 encoding!'


def test_authenticate_edit_failed_upload():
    '''
    Testing that a file with no file name is not allowed to be uploaded
    '''
    backend = Backend()
    uploaded_file = io.BytesIO(b'test content')
    uploaded_file.filename = ''
    result = backend.authenticate_edit(uploaded_file, "", "", "test_user")
    assert result['success'] == False
    assert result['message'] == 'You can only have .txt files'



def test_get_reviews(backend):
    backend.reviews_bucket = MagicMock()

    # Test when the blob does not exist
    backend.reviews_bucket.blob.return_value.exists.return_value = False
    reviews = backend.get_reviews("test_restaurant")
    assert reviews == []

    # Test when the blob exists
    backend.reviews_bucket.blob.return_value.exists.return_value = True
    backend.reviews_bucket.blob.return_value.download_as_text.return_value = json.dumps(
        [{
            "username": "test_user",
            "rating": 4
        }])
    reviews = backend.get_reviews("test_restaurant")
    assert reviews == [{"username": "test_user", "rating": 4}]


def test_add_review(backend):
    backend.reviews_bucket = MagicMock()
    backend.get_reviews = MagicMock(return_value=[{
        "username": "test_user",
        "rating": 4
    }])

    backend.add_review("test_restaurant", "another_user", 5)

    backend.reviews_bucket.blob.return_value.upload_from_string.assert_called_once_with(
        json.dumps([{
            "username": "test_user",
            "rating": 4
        }, {
            "username": "another_user",
            "rating": 5
        }]))


def test_get_average_rating(backend):
    backend.get_reviews = MagicMock()

    # Test when there are no reviews
    backend.get_reviews.return_value = []
    average_rating = backend.get_average_rating("test_restaurant")
    assert average_rating == 0

    # Test when there are reviews
    backend.get_reviews.return_value = [{
        "username": "test_user",
        "rating": 4
    }, {
        "username": "another_user",
        "rating": 5
    }]
    average_rating = backend.get_average_rating("test_restaurant")
    assert average_rating == 4.5
