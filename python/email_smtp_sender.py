#!/usr/bin/python3

import sys
import smtplib
from email.mime.text import MIMEText

# [ Constants ]
ENCODING = "utf-8"
MAIL = {
    "NOTICE": {"HOST": "", "USER": "", "PSWD": "", "SMTP_PORT": "", "ADDRESS": ""},
}
SUBJECT = ""
CONTENT = r"""
"""

# [ Functions ]
# Send email.
def send_email(email_address):
    msg = MIMEText("\n{}{}".format(email_address.split("@")[0], CONTENT).encode(ENCODING), 'plain', ENCODING)
    msg["Subject"] = SUBJECT
    msg["From"]    = MAIL["NOTICE"]["ADDRESS"]
    msg["To"]      = email_address
    msg["Bcc"]     = MAIL["NOTICE"]["ADDRESS"]

    smtp = smtplib.SMTP(MAIL["NOTICE"]["HOST"], MAIL["NOTICE"]["SMTP_PORT"])
    smtp.login(MAIL["NOTICE"]["USER"], MAIL["NOTICE"]["PSWD"])
    try:
        smtp.send_message(msg)
    finally:
        smtp.quit()

# [ MAIN ]
# Connect server.
# sys.argv[1] as to-address
if "@" in sys.argv[1]:
    print("[ {} ] will recieve an email.".format(sys.argv[1]))
    send_email(sys.argv[1])
else:
    print("email address as param is required.")

print("done.")
