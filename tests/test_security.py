import pytest

from src.security import (
    URLValidationError,
    safe_display_text,
    validate_url,
)


def test_accepts_valid_https_url():
    result = validate_url("https://example.com/login?next=home")

    assert result.normalized == "https://example.com/login?next=home"
    assert result.hostname == "example.com"
    assert result.scheme == "https"


def test_adds_https_when_scheme_is_missing():
    result = validate_url("example.com/path")

    assert result.normalized == "https://example.com/path"


def test_accepts_valid_ip_address():
    result = validate_url("http://192.0.2.1/check")

    assert result.hostname == "192.0.2.1"


@pytest.mark.parametrize("value", ["", "   "])
def test_rejects_empty_input(value):
    with pytest.raises(URLValidationError):
        validate_url(value)


def test_rejects_non_text_input():
    with pytest.raises(URLValidationError):
        validate_url(12345)


def test_rejects_excessively_long_input():
    value = "https://" + ("a" * 2048) + ".com"

    with pytest.raises(URLValidationError):
        validate_url(value)


def test_rejects_control_characters():
    with pytest.raises(URLValidationError):
        validate_url("https://example.com/\nadmin")


@pytest.mark.parametrize(
    "value",
    [
        "javascript:alert(1)",
        "data:text/html,<script>alert(1)</script>",
        "file:///etc/passwd",
        "ftp://example.com/file",
        "gopher://example.com",
    ],
)
def test_rejects_unsafe_schemes(value):
    with pytest.raises(URLValidationError):
        validate_url(value)


def test_rejects_embedded_credentials():
    with pytest.raises(URLValidationError):
        validate_url("https://user:secret@example.com")


def test_rejects_invalid_port():
    with pytest.raises(URLValidationError):
        validate_url("https://example.com:99999")


def test_rejects_spaces():
    with pytest.raises(URLValidationError):
        validate_url("https://exa mple.com")


def test_rejects_backslashes():
    with pytest.raises(URLValidationError):
        validate_url(r"https://example.com\@evil.com")


def test_rejects_invalid_percent_encoding():
    with pytest.raises(URLValidationError):
        validate_url("https://example.com/%zz")


def test_rejects_invalid_hostname():
    with pytest.raises(URLValidationError):
        validate_url("https://-bad.example")


def test_escapes_untrusted_display_text():
    result = safe_display_text('<script>alert("x")</script>')

    assert result == (
        "&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;"
    )