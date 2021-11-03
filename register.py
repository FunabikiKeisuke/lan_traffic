import sqlite3 as sqlite3
import os as os
import re as re

dbname = '/mnt/hdd/db/device.db'

conn = sqlite3.connect(dbname)
cursor = conn.cursor()


def make_table():
    create_table = 'CREATE TABLE devices (device varchar(64), mac varchar(17), ip varchar(15))'
    cursor.execute(create_table)


def insert_device():
    print('-' * 50)
    print('端末を登録します')
    device = check_device()
    if device == -1:
        print('登録をキャンセルしました')
        return

    mac = check_mac()
    if mac == -1:
        print('登録をキャンセルしました')
        return

    ip = check_ip()
    if ip == -1:
        print('登録をキャンセルしました')
        return

    data = [device, mac, ip]

    if cursor.execute('INSERT INTO devices (device, mac, ip) VALUES (?, ?, ?)', data):
        conn.commit()
        cursor.execute('SELECT * FROM devices WHERE mac=?', [mac])
        in_device = cursor.fetchall()[0]
        print('-' * 50)
        print('以下の内容で登録しました')
        print(f"登録名　   ：{in_device[0]}")
        print(f"MACアドレス：{in_device[1]}")
        print(f"IPアドレス ：{in_device[2]}")


def check_device():
    while True:
        device = input('登録名\n>>')
        print("\n")

        # cancel
        if device == 'n':
            return -1

        cursor.execute('SELECT * FROM devices WHERE device=?', [device])
        if len(cursor.fetchall()) == 0:
            return device
        else:
            print(f"`{device}`は既に登録されています")
            print("別の名前で登録して下さい")
            print("※キャンセルする場合は`n`を入力")


def check_mac():
    while True:
        mac = input('MACアドレス\n>>')
        print("\n")

        # cancel
        if mac == 'n':
            return -1

        if re.match(r"..:..:..:..:..:..$", mac):
            return mac
        else:
            print("MACアドレスの形式が不正です")
            print("もう一度入力して下さい")
            print("※キャンセルする場合は`n`を入力")


def check_ip():
    while True:
        ip = input('IPアドレス\n>>')
        print("\n")

        # cancel
        if ip == 'n':
            return -1

        if re.match(r"[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$", ip):
            return ip
        else:
            print("IPアドレスの形式が不正です")
            print("もう一度入力して下さい")
            print("※キャンセルする場合は`n`を入力")


def get_device():
    print('-' * 50)
    print('登録済み端末一覧')
    cursor.execute('SELECT * FROM devices')
    for device in cursor.fetchall():
        print(f"登録名：{device[0]},\tMACアドレス：{device[1]},\tIPアドレス：{device[2]}")


def delete_device():
    print('-' * 50)
    print('端末を削除します')
    get_device()

    while True:
        device = input("削除する端末の登録名を入力して下さい\n※キャンセルする場合は`n`を入力\n>>")
        if device == 'n':
            print("端末削除をキャンセルしました")
            break

        cursor.execute('SELECT device FROM devices WHERE device=?', [device])
        if not len(cursor.fetchall()) == 0:
            if cursor.execute('DELETE FROM devices WHERE device=?', [device]):
                conn.commit()
                print(f"`{device}`を削除しました")
                break
        else:
            print(f"`{device}`はデータベースに存在しません")


def update_device():
    print('-' * 50)
    print("端末を更新します")
    get_device()

    while True:
        device = input("更新する端末の登録名を入力して下さい\n※キャンセルする場合は`n`を入力\n>>")
        if device == 'n':
            print('端末更新をキャンセルしました')
            break

        cursor.execute('SELECT device FROM devices WHERE device=?', [device])
        if not len(cursor.fetchall()) == 0:
            mac = check_mac()
            if mac == -1:
                print("更新をキャンセルしました")
                return

            ip = check_ip()
            if ip == -1:
                print("更新をキャンセルしました")
                return

            if cursor.execute('UPDATE devices SET mac=?, ip=? WHERE device=?', [mac, ip, device]):
                conn.commit()
                print('以下の内容で更新しました')
                print(f"登録名　   ：{device}")
                print(f"MACアドレス：{mac}")
                print(f"IPアドレス ：{ip}")
                break
        else:
            print(f"`{device}`はデータベースに存在しません")


if __name__ == '__main__':
    # テーブルが存在しないときは作成する
    cursor.execute("SELECT * FROM sqlite_master WHERE type='table'")
    if len(cursor.fetchall()) == 0:
        make_table()
        print('テーブルを作成しました')
        print('-' * 50)

    while True:
        try:
            ans = int(input('登録済みの端末の表示：1\n'
                            '端末登録　　　　　　：2\n'
                            '端末削除　　　　　　：3\n'
                            '端末更新　　　　　　：4\n'
                            '何もしない　　　　　：5\n>>'))
        except:
            ans = -1

        if ans == 1:
            get_device()
        elif ans == 2:
            insert_device()
        elif ans == 3:
            delete_device()
        elif ans == 4:
            update_device()
        else:
            break

        print('-' * 50)

    conn.close()
