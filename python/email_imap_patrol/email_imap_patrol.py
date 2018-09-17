#!/usr/bin/python3

# [ How to setup CentOS 7 ]
# yum install centos-release-scl
# yum install rh-python36
# scl enable rh-python36 bash
# [ How to run ]
# python3 email_imap_patrol.py

import sys, os, datetime, json
import imaplib, email

# [ Constants ]
CONF_JSON = "conf.json"
DELETE_LOG = "delete.log"

# [ Functions ]
# システム設定を取得する
def get_conf():
    # ファイル存在をチェックする
    if not os.path.isfile(CONF_JSON):
        print("[Error] File not found: {}".format(CONF_JSON))
        return 1

    with open(CONF_JSON) as f:
        conf = json.load(f)
    print("Conf loaded.")
    
    # ファイル内容の妥当性をチェックする
    if not "connection" in conf:
        print("[Error] Json obj not found: connection")
        return 2
    if not "condition" in conf:
        print("[Error] Json obj not found: condition")
        return 3
    # キーワード設定から空行ならびに空白行を削除する
    conf["condition"]["keywords"] = [x.strip() for x in conf["condition"]["keywords"] if x.strip() != ""]
    if len(conf["condition"]["keywords"]) == 0:
        print("[Error] No valid condition keywords")
        return 4
    if not "since" in conf["condition"]:
        print("[Warn] No delete log")
    
    return conf

# サーバーへの接続を取得する
def get_conn(conf):
    # サーバに接続する
    try:
        conn = imaplib.IMAP4_SSL(conf["server"], conf["port"])
    except:
        print("[Error] Failed to connect")
        return 10
    print("Connected.")
    # 認証を行う
    try:
        conn.login(conf["uid"], conf["pwd"])
    except:
        print("[Error] Failed to log in")
        return 11
    # 受信箱を選択する
    try:
        conn.select('INBOX')
    except:
        print("[Error] Failed to select INBOX")
        return 12
    print("Logged in.")
    return conn

# 不要メールを検索して削除する
def patrol(conn, cond):
    head, data = conn.search(None, '(UNSEEN)', '(SINCE {})'.format(cond["since"]))

    # 取得したメール一覧の処理を行う
    delete_logs = []
    for num in data[0].split():
        h, d = conn.fetch(num, '(RFC822)')
        raw_email = d[0][1]
        msg = email.message_from_string(raw_email.decode('utf-8'))
        # 文字コードを取得する
        msg_encoding = email.header.decode_header(msg.get('Subject'))[0][1] or 'iso-2022-jp'
        # 件名を取得する
        msg_subject = email.header.decode_header(msg.get('Subject'))[0][0]
        if isinstance(msg_subject, str):
            subject = msg_subject
        else:
            subject = str(msg_subject.decode(msg_encoding))
        # 本文を取得する
        body = msg.get_payload()
        # キーワードにマッチするかどうかをチェックする
        for k in cond["keywords"]:
            if k in "{}\n{}".format(subject, body):
                # メールを削除する
                conn.store(num, '+FLAGS', '\\Deleted')
                conn.expunge()
                # 削除履歴を更新する
                delete_logs.append("[date]{} [from]{} [subject]{} [keyword]{}".format(msg["Date"], msg["From"], subject, k))
                break

    # 削除履歴を記録する
    print("{} message[s] deleted".format(len(delete_logs)))
    with open(DELETE_LOG, "a") as f:
        f.write(os.linesep.join(delete_logs))

# [ MAIN ]
def main():
    conf = get_conf()
    if isinstance(conf, int):
        sys.exit(conf) 
    
    conn = get_conn(conf["connection"])
    if isinstance(conn, int):
        sys.exit(conn)
    
    # 次回実行時の SINCE 条件として実行時刻を記憶する
    since = datetime.datetime.now().strftime("%d-%b-%Y")

    patrol(conn, conf["condition"])
    conn.close()
    conn.logout()
    
    # 実行時刻を更新する
    conf["condition"]["since"] = since
    with open(CONF_JSON, "w") as f:
        json.dump(conf, f, indent=4)

if __name__ == '__main__':
    main()

