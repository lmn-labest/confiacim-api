import pytest
from freezegun import freeze_time
from jwt import ExpiredSignatureError, decode

from confiacim_api.conf import settings
from confiacim_api.security import create_access_token, get_password_hash, verify_password

PASSWORD = "123456"


@pytest.fixture
def password_hashed():
    return get_password_hash(PASSWORD)


@pytest.mark.unit
def test_get_password_hash_is_not_the_same_as_password():
    password_hash = get_password_hash(PASSWORD)
    assert password_hash != PASSWORD


@pytest.mark.unit
def test_positive_verify_password(password_hashed):
    assert verify_password(PASSWORD, password_hashed)


@pytest.mark.unit
def test_negative_verify_password_wrong_password(password_hashed):
    assert verify_password(PASSWORD + "!!", password_hashed) is False


@pytest.mark.unit
def test_jwt():
    data = {"test": "test"}

    token = create_access_token(data)

    decoded = decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])

    assert decoded["test"] == data["test"]
    assert decoded["exp"]


@pytest.mark.unit
def test_expire_time_jwt():
    data = {"test": "test"}

    with freeze_time("2012-01-14 01:00:00"):
        token = create_access_token(data)

    with freeze_time("2012-01-14 02:00:00"):
        with pytest.raises(ExpiredSignatureError):
            decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])