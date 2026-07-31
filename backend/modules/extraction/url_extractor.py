"""URL text extraction (Section 3.2.1: BeautifulSoup, meaningful text only)."""
import ipaddress
import socket
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

REQUEST_TIMEOUT_SECONDS = 10
MAX_RESPONSE_BYTES = 10 * 1024 * 1024
NOISE_TAGS = ("script", "style", "noscript", "header", "footer", "nav", "svg")


class UnsafeURLError(ValueError):
    pass


def _assert_public_url(url: str) -> None:
    """Blocks requests to loopback/private/link-local hosts to prevent SSRF."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise UnsafeURLError("Only http/https URLs are supported.")
    if not parsed.hostname:
        raise UnsafeURLError("URL is missing a hostname.")

    try:
        addr_infos = socket.getaddrinfo(parsed.hostname, None)
    except socket.gaierror as exc:
        raise UnsafeURLError(f"Could not resolve host: {parsed.hostname}") from exc

    for family, _, _, _, sockaddr in addr_infos:
        ip = ipaddress.ip_address(sockaddr[0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise UnsafeURLError("URL resolves to a non-public address.")


def extract_url_text(url: str) -> str:
    _assert_public_url(url)

    response = requests.get(
        url,
        timeout=REQUEST_TIMEOUT_SECONDS,
        stream=True,
        headers={"User-Agent": "EduDell/1.0 (+educational content extraction)"},
    )
    response.raise_for_status()

    content = response.raw.read(MAX_RESPONSE_BYTES + 1, decode_content=True)
    if len(content) > MAX_RESPONSE_BYTES:
        raise ValueError("Remote content exceeds maximum allowed size.")

    soup = BeautifulSoup(content, "html.parser")
    for tag in soup(NOISE_TAGS):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)
