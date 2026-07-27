"""Local URL preparation for the machine-learning model."""

import ipaddress
from urllib.parse import urlsplit


def canonicalize_url_for_model(value: str) -> str:
    """
    Create a consistent URL representation.

    This function:
    - performs no network request;
    - removes HTTP/HTTPS;
    - removes a leading www.;
    - keeps the hostname, non-default port, path, query and fragment.
    """

    if not isinstance(value, str):
        return ""

    text = value.strip()

    if not text:
        return ""

    candidate = text

    if "://" not in candidate:
        candidate = f"https://{candidate}"

    try:
        parsed = urlsplit(candidate)
    except ValueError:
        return text.lower()

    hostname = parsed.hostname

    if not hostname:
        return text.lower()

    hostname = hostname.lower().rstrip(".")

    if hostname.startswith("www."):
        hostname = hostname[4:]

    try:
        hostname = hostname.encode("idna").decode("ascii")
    except UnicodeError:
        return text.lower()

    try:
        address = ipaddress.ip_address(hostname)

        if address.version == 6:
            hostname = f"[{hostname}]"
    except ValueError:
        pass

    try:
        port = parsed.port
    except ValueError:
        return text.lower()

    scheme = parsed.scheme.lower()
    default_port = (
        (scheme == "http" and port == 80)
        or (scheme == "https" and port == 443)
    )

    port_text = ""

    if port is not None and not default_port:
        port_text = f":{port}"

    path = parsed.path or "/"
    query = f"?{parsed.query}" if parsed.query else ""
    fragment = f"#{parsed.fragment}" if parsed.fragment else ""

    return f"{hostname}{port_text}{path}{query}{fragment}"

def canonicalize_urls_for_model(values):
    """Canonicalize a collection of URLs for scikit-learn."""

    return [
        canonicalize_url_for_model(str(value))
        for value in values
    ]