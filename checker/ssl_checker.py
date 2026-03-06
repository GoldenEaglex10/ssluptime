import ssl
import socket
from urllib.parse import urlparse
from datetime import datetime, timezone


def check_ssl_expiry(domain):
    try:
        hostname = urlparse(domain).hostname
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                expiry_date = expiry_date.replace(tzinfo=timezone.utc)
                return (expiry_date - datetime.now(timezone.utc)).days
    except Exception as e:
        return f"SSL check failed: {str(e)}"
