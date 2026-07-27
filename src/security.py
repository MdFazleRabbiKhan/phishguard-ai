"""Security controls for user-supplied URL text."""

from dataclasses import dataclass
from html import escape
import ipaddress
import re
from urllib.parse import urlsplit


MIN_URL_LENGTH = 4
MAX_URL_LENGTH = 2048
ALLOWED_SCHEMES = {"http", "https"}

BLOCKED_PREFIXES = (
    "javascript:",
    "data:",
    "file:",
    "ftp:",
    "mailto:",
    "vbscript:",
    "gopher:",
)

DOMAIN_LABEL_PATTERN = re.compile(r"^[A-Za-z0-9-]+$")
INVALID_PERCENT_PATTERN = re.compile(r"%(?![0-9A-Fa-f]{2})")


class URLValidationError(ValueError):
    """Raised when a URL fails security validation."""


@dataclass(frozen=True)
class ValidatedURL:
    """A URL that passed all security checks."""

    original: str
    normalized: str
    scheme: str
    hostname: str
    port: int | None


def _validate_hostname(hostname: str) -> None:
    """Validate an IP address or domain name locally."""

    if len(hostname) > 253:
        raise URLValidationError("Hostname is too long.")

    try:
        ipaddress.ip_address(hostname)
        return
    except ValueError:
        pass

    try:
        ascii_hostname = hostname.encode("idna").decode("ascii").rstrip(".")
    except UnicodeError as error:
        raise URLValidationError(
            "Hostname contains invalid characters."
        ) from error

    if not ascii_hostname:
        raise URLValidationError("Hostname is missing.")

    for label in ascii_hostname.split("."):
        if (
            not label
            or len(label) > 63
            or not DOMAIN_LABEL_PATTERN.fullmatch(label)
            or label.startswith("-")
            or label.endswith("-")
        ):
            raise URLValidationError("Hostname format is invalid.")


def validate_url(value: str) -> ValidatedURL:
    """Validate URL text without visiting the website."""

    if not isinstance(value, str):
        raise URLValidationError("URL must be text.")

    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise URLValidationError("URL contains control characters.")

    original = value
    text = value.strip()

    if not text:
        raise URLValidationError("URL cannot be empty.")

    if not MIN_URL_LENGTH <= len(text) <= MAX_URL_LENGTH:
        raise URLValidationError(
            f"URL length must be between "
            f"{MIN_URL_LENGTH} and {MAX_URL_LENGTH} characters."
        )

    if any(character.isspace() for character in text):
        raise URLValidationError("URL cannot contain spaces.")

    if "\\" in text:
        raise URLValidationError("Backslashes are not allowed in URLs.")

    if INVALID_PERCENT_PATTERN.search(text):
        raise URLValidationError("URL contains invalid percent encoding.")

    if text.lower().startswith(BLOCKED_PREFIXES):
        raise URLValidationError("Only HTTP and HTTPS URLs are allowed.")

    if "://" not in text:
        text = f"https://{text}"

    try:
        parsed = urlsplit(text)
    except ValueError as error:
        raise URLValidationError("URL format is invalid.") from error

    scheme = parsed.scheme.lower()

    if scheme not in ALLOWED_SCHEMES:
        raise URLValidationError("Only HTTP and HTTPS URLs are allowed.")

    if not parsed.netloc:
        raise URLValidationError("URL hostname is missing.")

    if parsed.username is not None or parsed.password is not None:
        raise URLValidationError(
            "Usernames and passwords are not allowed inside URLs."
        )

    try:
        hostname = parsed.hostname
        port = parsed.port
    except ValueError as error:
        raise URLValidationError(
            "URL port or hostname is invalid."
        ) from error

    if not hostname:
        raise URLValidationError("URL hostname is missing.")

    _validate_hostname(hostname)

    normalized = f"{scheme}://{text.split('://', 1)[1]}"

    return ValidatedURL(
        original=original,
        normalized=normalized,
        scheme=scheme,
        hostname=hostname.lower(),
        port=port,
    )


def safe_display_text(value: str) -> str:
    """Escape HTML characters before displaying untrusted text."""

    return escape(str(value), quote=True)