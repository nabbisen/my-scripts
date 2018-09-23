#!/usr/bin/python3

# [ How to setup CentOS 7 ]
# yum install centos-release-scl
# yum install rh-python36
# scl enable rh-python36 bash
# [ How to setup chardet ]
# pip3 [or simply `pip` if it uses `python3`] install chardet
# * ref: https://pypi.org/project/chardet/
# [ How to run ]
# python3 email_imap_patrol.py

import sys, os, datetime, json
import imaplib, email
import chardet

# [ Constants ]
CONF_JSON = "conf.json"
DELETE_LOG = "delete.log"

# [ Functions ]
# システム設定を取得する
def get_conf():
    # ファイル存在をチェックする
    if not os.path.isfile(CONF_JSON):
        print("[Error] File not found: {} .".format(CONF_JSON))
        return 1

    with open(CONF_JSON) as f:
        conf = json.load(f)
    print("Conf loaded.")
    
    # ファイル内容の妥当性をチェックする
    if not "connection" in conf:
        print("[Error] Json obj not found: connection.")
        return 2
    if not "condition" in conf:
        print("[Error] Json obj not found: condition.")
        return 3

    # キーワード設定のデータ構造を最適化する
    cond_list = []
    for kgrp in conf["condition"]["keywords"]:
        if not isinstance(kgrp, list):
            kgrp_mod = [str(kgrp)]
        else:
            kgrp_mod = kgrp
        # キーワード設定から空行ならびに空白行を削除する
        kgrp_mod = [x for x in kgrp_mod if x.strip() != ""]
        # キーワードの重複を削除する
        kgrp_mod_uniq = []
        for k in kgrp_mod:
            if not k in kgrp_mod_uniq:
                kgrp_mod_uniq.append(k)
        kgrp_mod = kgrp_mod_uniq
        # 有効なキーワードが存在する場合
        if 0 < len(kgrp_mod):
            cond_list.append(kgrp_mod)
    # キーワードのグループの重複を削除する（ただし処理の簡素化のためにグループ内の要素の並び順まで同じもののみを削除対象とする）
    cond_list_uniq = []
    for kgrp in cond_list:
        if not kgrp in cond_list_uniq:
            cond_list_uniq.append(kgrp)
    cond_list = cond_list_uniq
    # 有効なキーワードのグループが存在する場合
    if len(cond_list) == 0:
        print("[Error] No valid keywords in condition.")
        return 4
    conf["condition"]["keywords"] = cond_list

    if not "since" in conf["condition"]:
        print("[Warn] No delete log.")
    
    return conf

# サーバーへの接続を取得する
def get_conn(conf):
    # サーバに接続する
    try:
        conn = imaplib.IMAP4_SSL(conf["server"], conf["port"])
    except:
        print("[Error] Failed to connect.")
        return 10
    print("Connected.")
    # 認証を行う
    try:
        conn.login(conf["uid"], conf["pwd"])
    except:
        print("[Error] Failed to log in.")
        return 11
    # 受信箱を選択する
    try:
        conn.select("Inbox")
    except:
        print("[Error] Failed to select Inbox.")
        return 12
    print("Logged in.")
    return conn

# 不要メールを検索して削除する
def patrol(conn, cond):
    if "since" in cond:
        head, data = conn.search(None, "UNSEEN SINCE {}".format(cond["since"]))
    else:
        head, data = conn.search(None, "UNSEEN")

    # 取得したメール一覧の処理を行う
    msg_nums = data[0].split()
    print("{} message[s] found.".format(len(msg_nums)))
    delete_logs = []
    for num in msg_nums:
        h, d = conn.fetch(num, "(RFC822)")
        # fetch コマンドによってメールに自動的に \\SEEN フラグが付与されるため、このフラグを削除して未読状態に戻す
        conn.store(num, "-FLAGS", "\\Seen")

        raw_email = d[0][1]

        msg = email.message_from_string(raw_email.decode("utf-8"))
        # 文字コードを取得する
        msg_encoding = email.header.decode_header(msg.get("Subject"))[0][1] or "iso-2022-jp"
        # 件名と本文を取得する
        raw_subject = email.header.decode_header(msg.get("Subject"))[0][0]
        if isinstance(raw_subject, str):
            subject = raw_subject
        else:
            subject = str(raw_subject.decode(msg_encoding))
        # 本文を取得する
        raw_body = msg.get_payload(decode=True)
        body = raw_body.decode(chardet.detect(raw_body)["encoding"])
        # for debug:
        #print(subject, body)

        # キーワードにマッチするかどうかをチェックする
        is_delete_target = False
        for kgrp in cond["keywords"]:
            # キーワード単位に AND 判定を行う
            is_delete_candidate = True
            for k in kgrp:
                if not k in "{}\n{}".format(subject, body):
                    is_delete_candidate = False
                    break
            # キーワードのグループ単位に OR 判定を行う
            if is_delete_candidate == True:
                is_delete_target = True
                delele_kgrp = kgrp
                break
        if is_delete_target == True:
            # メールに削除フラグ＋既読フラグを付与する
            conn.store(num, "+FLAGS", "\\Deleted")
            conn.store(num, "+FLAGS", "\\Seen")
            # 削除履歴を更新する
            delete_logs.append("date={}, from={}, subject]={}, keyword[s]={}".format(msg["Date"], msg["From"], subject, " AND ".join(["\"" + x + "\"" for x in delele_kgrp])))

    # # 削除フラグの立っているメールを物理削除する
    # （本プログラム以外で削除フラグが立てられた場合にも該当する。予期せぬ動作を避けるため、コメントアウトして動作しないようにする）
    # conn.expunge()

    # 削除履歴を記録する
    print("{} message[s] deleted.".format(len(delete_logs)))
    if 0 < len(delete_logs):
        with open(DELETE_LOG, "a+") as f:
            f.write("\n".join(delete_logs) + "\n")

# [ MAIN ]
def main():
    print("=== System start: {} ===".format(datetime.datetime.now().strftime("%x %X")))
    conf = get_conf()
    if isinstance(conf, int):
        sys.exit(conf) 
    
    conn = get_conn(conf["connection"])
    if isinstance(conn, int):
        sys.exit(conn)
    
    # 次回実行時の SINCE 条件として実行日を記憶する
    since = datetime.datetime.now().strftime("%d-%b-%Y")

    patrol(conn, conf["condition"])
    conn.close()
    conn.logout()
    
    # 実行日を更新する
    conf["condition"]["since"] = since
    with open(CONF_JSON, "w") as f:
        json.dump(conf, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
