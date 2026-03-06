import requests
import re

# Only the patterns that truly indicate the site is broken
HTML_CRITICAL_ERRORS = [
    r"error establishing a database connection",
    r"database error",
    r"fatal error",
    r"uncaught exception",
    r"internal server error",
    r"service unavailable",
    r"502 bad gateway",
    r"504 gateway timeout",
]


def check_site_uptime(domain):
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/115.0 Safari/537.36"
            )
        }

        response = requests.get(domain, timeout=20, allow_redirects=True, headers=headers)
        status = response.status_code
        body = response.text.lower()

        # ---------------------------------------------------------------------
        # 1. TRUE DOWNTIME CHECK (connection problems always mean down)
        # ---------------------------------------------------------------------
        if status >= 500:
            return "Critical: Server Error"

        # ---------------------------------------------------------------------
        # 2. HTML CONTENT BASED CRITICAL FAILURE
        # Only match REAL breakages like DB errors or fatal exceptions.
        # ---------------------------------------------------------------------
        for pattern in HTML_CRITICAL_ERRORS:
            if re.search(pattern, body):
                return f"Critical: HTML Error ({pattern})"

        # ---------------------------------------------------------------------
        # 3. If site loads at all (status 200-499), we consider it UP
        # ---------------------------------------------------------------------

        # Status 200 OK = SITE UP
        if status == 200:
            return "Up"

        # 301/302 Redirects → Up (no alerts)
        if 300 <= status < 400:
            return "Up"

        # 401/403/404/4xx → Up (site reachable)
        if 400 <= status < 500:
            return "Up"

        # If we get here, default to Up
        return "Up"

    # -------------------------------------------------------------------------
    # CONNECTION ERRORS = DOWNTIME
    # -------------------------------------------------------------------------
    except requests.exceptions.SSLError as e:
        return f"Critical: SSL Error ({str(e)})"

    except requests.exceptions.ConnectTimeout:
        return "Critical: Connection Timeout"

    except requests.exceptions.ReadTimeout:
        return "Critical: Read Timeout"

    except requests.exceptions.ConnectionError as e:
        return f"Critical: Connection Error ({str(e)})"

    except requests.RequestException as e:
        return f"Critical: Request Error ({str(e)})"
