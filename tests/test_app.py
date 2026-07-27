"""Automated tests for the Streamlit interface."""

from streamlit.testing.v1 import AppTest


def create_app():
    """Create a test instance of the Streamlit application."""
    return AppTest.from_file("app/streamlit_app.py")


def test_app_loads_without_error():
    app = create_app()
    app.run()

    assert not app.exception
    assert app.title[0].value == "🛡️ PhishGuard AI"
    assert "never opened or visited" in app.info[0].value


def test_empty_url_is_rejected():
    app = create_app()
    app.run()

    app.button[0].click()
    app.run()

    assert not app.exception
    assert app.warning[0].value == "Please enter a URL."