import pytest

from src.features import canonicalize_url_for_model


def test_www_and_non_www_versions_are_identical():
    without_www = canonicalize_url_for_model(
        "https://example.com/login"
    )
    with_www = canonicalize_url_for_model(
        "https://www.example.com/login"
    )

    assert without_www == with_www
    assert without_www == "example.com/login"


def test_http_and_https_versions_are_identical():
    http_result = canonicalize_url_for_model(
        "http://example.com/path"
    )
    https_result = canonicalize_url_for_model(
        "https://example.com/path"
    )

    assert http_result == https_result


def test_retains_path_query_and_fragment():
    result = canonicalize_url_for_model(
        "https://www.Example.COM/Login?Next=Home#section"
    )

    assert result == "example.com/Login?Next=Home#section"


def test_works_when_scheme_is_missing():
    result = canonicalize_url_for_model("www.example.com/path")

    assert result == "example.com/path"


def test_preserves_non_default_port():
    result = canonicalize_url_for_model(
        "https://www.example.com:8443/login"
    )

    assert result == "example.com:8443/login"


@pytest.mark.parametrize(
    "value",
    [
        "http://www.example.com:80/path",
        "https://www.example.com:443/path",
    ],
)
def test_removes_default_ports(value):
    assert canonicalize_url_for_model(value) == "example.com/path"


def test_empty_input_returns_empty_text():
    assert canonicalize_url_for_model("") == ""


def test_canonicalizes_a_collection_of_urls():
    from src.features import canonicalize_urls_for_model

    results = canonicalize_urls_for_model(
        [
            "https://example.com/login",
            "https://www.example.com/login",
        ]
    )

    assert results == [
        "example.com/login",
        "example.com/login",
    ]