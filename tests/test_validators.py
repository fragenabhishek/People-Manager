"""Tests for the Validator utility class."""
import pytest

from utils.validators import ValidationError, Validator


def test_validate_required_passes():
    Validator.validate_required("hello", "Field")


def test_validate_required_empty_string():
    with pytest.raises(ValidationError, match="required"):
        Validator.validate_required("", "Field")


def test_validate_required_none():
    with pytest.raises(ValidationError, match="required"):
        Validator.validate_required(None, "Field")


def test_validate_min_length():
    Validator.validate_min_length("hello", 3, "Field")
    with pytest.raises(ValidationError, match="at least"):
        Validator.validate_min_length("hi", 3, "Field")


def test_validate_max_length():
    Validator.validate_max_length("hi", 10, "Field")
    with pytest.raises(ValidationError, match="exceed"):
        Validator.validate_max_length("a" * 11, 10, "Field")


def test_validate_email():
    Validator.validate_email("user@example.com")
    Validator.validate_email("")
    with pytest.raises(ValidationError, match="email"):
        Validator.validate_email("not-an-email")


def test_validate_password_match():
    Validator.validate_password_match("abc", "abc")
    with pytest.raises(ValidationError, match="match"):
        Validator.validate_password_match("abc", "xyz")


def test_validate_user_registration():
    Validator.validate_user_registration("user", "pass123", "pass123")
    with pytest.raises(ValidationError):
        Validator.validate_user_registration("", "pass123", "pass123")
    with pytest.raises(ValidationError):
        Validator.validate_user_registration("user", "12", "12")
    with pytest.raises(ValidationError):
        Validator.validate_user_registration("user", "pass123", "other123")


def test_validate_person_data():
    Validator.validate_person_data("Valid Name")
    with pytest.raises(ValidationError):
        Validator.validate_person_data("")
    with pytest.raises(ValidationError):
        Validator.validate_person_data("x" * 201)
