import os
import pytest

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from main import app, db, User


@pytest.fixture
def client():
    client = app.test_client()

    cleanup()  # clean up before every test

    db.create_all()

    yield client


def cleanup():
    # clean up/delete the DB (drop all tables in the database)
    db.drop_all()


# all test functions must start with test keyword
def test_index_not_logged_in(client):
    response = client.get("/")
    assert b"Enter your name" in response.data


def test_index_logged_in(client):
    # post request test
    client.post('/login',
                data={"user-name": "Test User", "user-email": "test@user.com",
                      "user-password": "password123"},
                follow_redirects=True)

    response = client.get('/')
    assert b"Enter your guess: " in response.data


def test_result_correct(client):
    client.post('/login',
                data={"user-name": "Test User", "user-email": "test@user.com",
                      "user-password": "password123"},
                follow_redirects=True)

    user = db.query(User).first()
    user.secret_num = 15  # set secret number to 15 so you can correctly guess
    user.save()

    response = client.post("/result",
                           data={"guess": 15})

    assert b"Congratulations 15 was the secret number!"


def test_result_incorrect_try_bigger(client):
    client.post('/login',
                data={"user-name": "Test User", "user-email": "test@user.com",
                      "user-password": "password123"},
                follow_redirects=True)

    user = db.query(User).first()
    user.secret_num = 15  # set secret number to 15 so you can correctly guess
    user.save()

    response = client.post("/result",
                           data={"guess": 10})

    assert b"try a number that's bigger than 10"


def test_result_incorrect_try_smaller(client):
    client.post('/login',
                data={"user-name": "Test User", "user-email": "test@user.com",
                      "user-password": "password123"},
                follow_redirects=True)

    user = db.query(User).first()
    user.secret_num = 15  # set secret number to 15 so you can correctly guess
    user.save()

    response = client.post("/result",
                           data={"guess": 20})

    assert b"try a number that's smaller than 20"


def test_profile(client):
    client.post('/login',
                data={"user-name": "Test User", "user-email": "test@user.com",
                      "user-password": "password123"},
                follow_redirects=True)

    response = client.get("/profile")

    assert b"Test User" in response.data


def test_profile_edit(client):
    client.post('/login',
                data={"user-name": "Test User", "user-email": "test@user.com",
                      "user-password": "password123"},
                follow_redirects=True)

    # GET
    response = client.get("/profile/edit")

    assert b"Edit your profile" in response.data

    # POST
    response = client.post("/profile/edit",
                           data={"profile-name": "Test User2", "profile-email": "testuser2@test.com"},
                           follow_redirects=True)

    assert b"Test User2" in response.data
    assert b"testuser2@test.com" in response.data


def test_profile_delete(client):
    client.post('/login',
                data={"user-name": "Test User", "user-email": "test@user.com",
                      "user-password": "password123"},
                follow_redirects=True)

    # GET
    response = client.get("/profile/delete")

    assert b"Delete your profile" in response.data

    # POST
    response = client.post("/profile/delete",
                           follow_redirects=True)

    assert b"Login" in response.data


def test_all_users(client):
    response = client.get('/users')
    assert b'Users' in response.data
    assert b'Test User' not in response.data  # Test User is not yet created

    # create a new user
    client.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                "user-password": "password123"}, follow_redirects=True)

    response = client.get('/users')
    assert b'Users' in response.data
    assert b'Test User' in response.data


def test_user_details(client):
    # create a new user
    client.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                "user-password": "password123"}, follow_redirects=True)

    # get user object from the database
    user = db.query(User).first()

    response = client.get('/user/{}'.format(user.id))
    assert b'test@user.com' in response.data
    assert b'Test User' in response.data

