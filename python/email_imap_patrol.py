#!/usr/bin/python3

import email
import email.header
from email.header import decode_header

# [ Constants ]
CONF = {
    "WATCH":  {"HOST": "[Your Host]", "USER": "[Your User]", "PSWD": "[Your Password]"},
    "NOTICE": {"HOST": "[Your Host]", "USER": "[Your User]", "PSWD": "[Your Password]", "SMTP_PORT": "[Your SMTP Port]", "ADDRESS": "[Your Email]"},
}

# [ Functions ]

# [ MAIN ]
# サーバに接続する
print("connected.")

# 認証を行う
print("logged in.")

spams = []
if 0 < len(warn_msgs):
    print("{} spams found.".format(str(len(warn_msgs))))
else:
    print("no spams found.")

print("done.")

sys.exit()
