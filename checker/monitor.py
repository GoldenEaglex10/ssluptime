from checker.ssl_checker import check_ssl_expiry
from checker.uptime_checker import check_site_uptime
from checker.email_alerts import send_email_alert
from checker.database import (
    init_db, log_alert, is_issue_active, set_issue_active, clear_active_issue
)
from datetime import datetime
import os

SITES_FILE = os.path.join("config", "sites.txt")
LOG_FILE = os.path.join("logs", "checker.log")

# SSL alert days to prevent daily spam
SSL_ALERT_DAYS = [30, 15, 7, 1]

# Delay clearing active issues (0.33 hours = 20 minutes)
CLEAR_COOLDOWN_HOURS = 0.33


def monitor_sites():
    init_db()

    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, 'w').close()

    with open(SITES_FILE) as f:
        sites = [line.strip() for line in f if line.strip()]

    with open(LOG_FILE, 'a') as log:
        log.write(f"\n--- Run at {datetime.now()} ---\n")

        for site in sites:
            ssl_result = check_ssl_expiry(site)
            uptime_result = check_site_uptime(site)

            current_issue = None  # tuple: (issue_type, details)

            # ================================================================
            #                        SSL CHECK
            # ================================================================
            if isinstance(ssl_result, int):
                # Only issue alerts on specific expiry milestones
                if ssl_result in SSL_ALERT_DAYS:
                    current_issue = (
                        "SSL Expiry Warning",
                        f"SSL certificate expires in {ssl_result} days."
                    )
            else:
                # SSL error always critical
                current_issue = ("SSL Error", ssl_result)

            # ================================================================
            #                        UPTIME CHECK
            # ================================================================
            # Only trigger alerts for true critical problems
            if uptime_result.startswith("Critical"):
                current_issue = ("Downtime", uptime_result)

            # ================================================================
            #                   ISSUE HANDLING / ALERT LOGIC
            # ================================================================
            if current_issue:
                alert_type, details = current_issue

                # Only send alert if not already active (prevents spam)
                if not is_issue_active(site, alert_type, details):
                    log_alert(site, alert_type, details)

                    send_email_alert(
                        domain=site,
                        issue_type=alert_type,
                        details=details
                    )

                    set_issue_active(site, alert_type, details)

            else:
                # If site is healthy → only clear if stable long enough
                try:
                    if not is_issue_active(site, "Downtime", "", CLEAR_COOLDOWN_HOURS):
                        clear_active_issue(site)
                except TypeError:
                    # Older DB function fallback
                    clear_active_issue(site)

            # ================================================================
            #                           LOGGING
            # ================================================================
            log_line = f"{site} | SSL: {ssl_result} | Uptime: {uptime_result}\n"
            print(log_line.strip())
            log.write(log_line)
