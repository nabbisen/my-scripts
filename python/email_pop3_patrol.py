#!/usr/bin/python3

import poplib
import email
import email.header
from email.header import decode_header

# [ Constants ]
MAIL = {
    "WATCH":  {"HOST": "[Your Host]", "USER": "[Your User]", "PSWD": "[Your Password]"},
    "NOTICE": {"HOST": "[Your Host]", "USER": "[Your User]", "PSWD": "[Your Password]", "SMTP_PORT": "[Your SMTP Port]", "ADDRESS": "[Your Email]"},
}
TARGET_SUBJECT = "Email Subject"

# [ Functions ]
# メールのヘッダをデコードして文字列として取得する
def get_header(msg_top, name):
    header = ''
    if msg_top[name]:
        for tup in decode_header(str(msg_top[name])):
            if type(tup[0]) is bytes:
                charset = tup[1]
                if charset:
                    header += tup[0].decode(tup[1])
                else:
                    header += tup[0].decode()
            elif type(tup[0]) is str:
                header += tup[0]
    return header

# メールの本文をデコードして文字列として取得する
def get_content(msg):
    charset = msg.get_content_charset()
    payload = msg.get_payload(decode=True)
    try:
        if payload:
            if charset:
                return payload.decode(charset)
            else:
                return payload.decode()
        else:
            return ""
    except:
        # デコードできない場合は生データにフォールバック
        return payload

# 警告メールを検索する
def watch_warn():
    ret = []

    # メールボックス内のメールの総数を取得する
    count = len(cli.list()[1])
    print("{} messages are found.".format(str(count)))
    
    # メールを検索する
    try:
        for i in range(count):
            no = i + 1
            # TOPコマンドでヘッダのみを受信する
            content = cli.top(no, 0)[1]
            msg_top = email.message_from_bytes(b"\r\n".join(content))
            subject = get_header(msg_top, "subject")
            if TARGET_SUBJECT in subject:
                msg_retr = cli.retr(no)[1]
                msg = email.message_from_bytes(b'\r\n'.join(msg_retr))
                warn_msg = "[ {} ]\n\non {}\n\n{}".format(get_header(msg_top, "from"), get_header(msg_top, "date"), get_content(msg))
                ret.append(warn_msg)
    finally:
        # 最後に必ず QUIT する
        cli.quit()

    ret.sort()
    
    for i in range(len(ret)):
        ret[i] = "{}\n\n... # {} over.".format(ret[i], str(i + 1))
    
    return ret

# 警告メールを転送する
import smtplib
from email.message import EmailMessage
def notice_warn(warn_msgs):
    msg = EmailMessage()
    msg["Subject"] = "{} （自動転送）".format(TARGET_SUBJECT)
    msg["From"]    = MAIL["NOTICE"]["ADDRESS"]
    msg["To"]      = MAIL["NOTICE"]["ADDRESS"]
    msg.set_content("\n\n\n---\n\n\n".join(warn_msgs))

    smtp = smtplib.SMTP(MAIL["NOTICE"]["HOST"], MAIL["NOTICE"]["SMTP_PORT"])
    smtp.login(MAIL["NOTICE"]["USER"], MAIL["NOTICE"]["PSWD"])
    try:
        smtp.send_message(msg)
    finally:
        smtp.quit()

# [ MAIN ]
# サーバに接続する
cli = poplib.POP3(MAIL["WATCH"]["HOST"])
print("connected.")

# 認証を行う
cli.user(MAIL["WATCH"]["USER"])
cli.pass_(MAIL["WATCH"]["PSWD"])
print("logged in.")

warn_msgs = watch_warn()
if 0 < len(warn_msgs):
    print("{} warnings found.".format(str(len(warn_msgs))))
    notice_warn(warn_msgs)
    print("noticed.")
else:
    print("no warnings found.")

print("done.")
