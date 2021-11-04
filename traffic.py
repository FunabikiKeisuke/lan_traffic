import sqlite3
import subprocess
import os
import re

traffic_db = '/mnt/hdd/db/traffic.db'
device_db = '/mnt/hdd/db/device.db'

traffic_conn = sqlite3.connect(traffic_db)
traffic_cursor = traffic_conn.cursor()
device_conn = sqlite3.connect(device_db)
device_cursor = device_conn.cursor()


def make_table():
    traffic_cursor.execute("SELECT * FROM sqlite_master WHERE type='table'")

    if len(traffic_cursor.fetchall()) == 0:
        create_table = 'CREATE TABLE log (date varchar(12), device varchar(64), upload int(256), download int(256))'
        traffic_cursor.execute(create_table)
        print("テーブルを作成しました")
        print('-' * 50)


def get_log():
    traffic_cursor.execute('SELECT * FROM log')

    for traffic in traffic_cursor.fetchall():
        print(f"{traffic[0]}\t{traffic[1]}\t{traffic[2]}\t{traffic[3]}\t{traffic[4]}")


def get_device():
    device_cursor.execute('SELECT * FROM devices')
    return device_cursor.fetchall()


def get_conversations(devices):
    data_dir = '/mnt/hdd/traffic_data/'
    latest_file = sorted(os.listdir(data_dir), reverse=True)
    if len(latest_file) == 0:
        exit(0)
    elif len(latest_file) == 1:
        latest_file = latest_file[0]
    else:
        latest_file = latest_file[1]
    date = f"{latest_file.replace('.pcap', '')}"

    cmd = f"tshark -r /mnt/hdd/traffic_data/{latest_file} -z conv,tcp -q"
    datas = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).communicate()[0].split(b'\n')[5:-3]

    shaping_dic = {}
    for data in datas:
        tmp = data.decode().split()
        fromIP = re.sub(':[0-9]+$', '', tmp[0])
        toIP = re.sub(':[0-9]+$', '', tmp[2])
        upload = int(tmp[6])
        download = int(tmp[4])

        for device in devices:
            if device[2] == fromIP:
                if device[0] in shaping_dic:
                    shaping_dic[device[0]][0] += upload
                    shaping_dic[device[0]][1] += download
                else:
                    shaping_dic[device[0]] = [upload, download]
                break

    shaping_data = []
    for device in shaping_dic:
        shaping_data.append([date, device, shaping_dic[device][0], shaping_dic[device][1]])

    return shaping_data


def reflect_data(datas):
    for data in datas:
        traffic_cursor.execute('INSERT INTO log (date, device, upload, download) VALUES (?, ?, ?, ?)', data)

    traffic_conn.commit()
    traffic_cursor.execute('SELECT * FROM log')
    for data in traffic_cursor.fetchall():
        print(data)


if __name__ == '__main__':
    make_table()
    devices = get_device()
    datas = get_conversations(devices)
    reflect_data(datas)

    traffic_conn.close()
    device_conn.close()
