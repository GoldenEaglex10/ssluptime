import subprocess
from datetime import datetime

# List of recipients
RECIPIENTS = [
    "itai@quatrohaus.com"
]

def send_email_alert(domain, issue_type, details=None):
    """
    Sends a formatted uptime alert to multiple recipients using Postfix.
    """

    # Format subject
    subject = f"[SSL Uptime Alert] Issue detected on {domain}"

    # Format message body
    message_lines = [
        "🚨 SSL / Uptime Monitoring Alert 🚨",
        "----------------------------------------",
        f"Domain: {domain}",
        f"Status: {issue_type}",
        f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    ]

    if details:
        message_lines.append(f"Details: {details}")

    message_lines.append("----------------------------------------")
    message_lines.append("Automated alert from SSL Uptime Checker.")
    message_lines.append("Please investigate the issue promptly.\n")

    message = "\n".join(message_lines)

    # Send to all recipients
    for email in RECIPIENTS:
        try:
            subprocess.run(
                ['mail', '-s', subject, email],
                input=message.encode(),
                check=True
            )
            print(f"[✔] Alert sent to {email}")
        except subprocess.CalledProcessError as e:
            print(f"[✖] Failed to send email to {email}: {e}")
