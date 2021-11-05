# lan_traffic
Raspberry Piを使ってLAN内のトラフィックを監視する．

## 必要なもの
- ポートミラーリング機能のあるスイッチングハブ
- Raspberry Pi
- Raspberry Piでキャプチャした`.pcap`ファイルを保存する外付けHDD

## ネットワーク図
![lan_network](https://raw.githubusercontent.com/FunabikiKeisuke/lan_traffic/main/lan_traffic.drawio.svg)

ここで図中の青実線は有線LAN，青破線は無線LANを示す．
スイッチングハブを経由して通信している端末のトラフィックを，スイッチングハブのポートミラーリング機能でRaspberry Piへミーラーリングする．
Wi-Fiルータは二重ルータを防ぐためにアクセスポイントモードにする必要がある．

## 使い方
### Wi-Fiルータをアクセスポイントモードで接続
モデムに接続したルータはルータモードに設定し，DHCPも有効にする．
スイッチングハブに接続したWi-Fiルータはアクセスポイントモード（またはブリッジモード）に設定し，DHCPは無効にする．

### スイッチングハブにポートミラーを設定
Raspberry Piと接続するポートをミラーリングポートとして設定する．
Wi-Fiルータを接続しているポートなど，トラフィックをキャプチャしたい機器を接続しているポートをポートミラーの対象として設定する．

### Raspberry PiのIPアドレスを固定
下記にRaspberry Pi OSの例を示す．

`/etc/dhcpcd.conf`に設定を追記．
```
pi@raspberrypi:~ $ sudo vi /etc/dhcpcd.conf
（略）
interface wlan0
static ip_address=192.168.0.3/24
static routers=192.168.0.1
static domain_name_servers=192.168.0.1
```
Raspberry Piを再起動して設定の反映を確認．
```
pi@raspberrypi:~ $ reboot
pi@raspberrypi:~ $ ifconfig
（略）
wlan0: flags=4163<UP,BROADCAST,MULTICAST>  mtu 1500
        inet 192.168.0.3  netmask 255.255.255.0  broadcast 192.168.0.255
（略）
```

### Raspberry Piに外付けHDDをマウント
下記にRaspberry Pi OSの例を示す．

HDDの認識を確認．
```
pi@raspberrypi:~ $ sudo fdisk -l | grep /dev/sda
Disk /dev/sda: 3.7 TiB, 4000752599040 bytes, 7813969920 sectors
/dev/sda1   2048 7813967871 7813965824  3.7T Microsoft basic data
```
HDDのUUIDとファイルシステムを確認．
```
pi@raspberrypi:~ $ sudo blkid /dev/sda1
/dev/sda1: LABEL="Elements" UUID="04F6232DF6231F04" TYPE="ntfs" PTTYPE="atari" PARTLABEL="Elements" PARTUUID="6d37ebe2-7815-4429-8743-f49e97b573c7"
```
`/mnt/hdd`にHDDを自動マウントするように`/etc/fstab`に追記．
```
pi@raspberrypi:~ $ sudo mkdir /mnt/hdd
pi@raspberrypi:~ $ sudo vi /etc/fstab
（略）
UUID="04F6232DF6231F04" /mnt/hdd    ntfs    defaults,nofail 0   0
```
Raspberry Piを再起動して自動マウントしていることを確認．
```
pi@raspberrypi:~ $ reboot
pi@raspberrypi:~ $ df -h | grep /dev/sda
/dev/sda1        3.7T   24G  3.7T    1% /mnt/hdd
```

### Raspberry Piでパケットをキャプチャ
下記にRaspberry Pi OSの例を示す．

必要なパッケージのインストール．
```
pi@raspberrypi:~ $ sudo apt update
pi@raspberrypi:~ $ sudo apt upgrade
pi@raspberrypi:~ $ sudo apt install tshark apache2 php libapache2-mod-php
```
本リポジトリをクローン．
```
pi@raspberrypi:~ $ git clone https://github.com/FunabikiKeisuke/lan_traffic.git
```
データベースを保存するディレクトリを作成．
```
pi@raspberrypi:~ $ sudo mkdir /mnt/hdd/db
```
ミラーリング対象端末のMACアドレスとIPアドレスを登録．
```
pi@raspberrypi:~ $ python3 lan_traffic/register.py
```
`.pcap`ファイルを保存するディレクトリを作成．
```
pi@raspberrypi:~ $ sudo mkdir /mnt/hdd/traffic_data
```
10分毎に`.pcap`ファイルを保存し，`.pcap`ファイルから通信量をデータベースに保存する設定を追記．
```
pi@raspberrypi:~ $ sudo crontab -e
（略）
*/10 * * * * bash /home/pi/lan_traffic/start_capture.sh
1,11,21,31,41,51 * * * * /usr/bin/python3 /home/pi/lan_traffic/traffic.py
```

### Raspberry Piで通信量を表示するWebサーバを立てる
下記にRaspberry Pi OSの例を示す．

`.html`ファイルをバックアップし，`.php`ファイルをコピー．
```
pi@raspberrypi:~ $ sudo mv /var/www/html/index.html /var/www/html/index.bak
pi@raspberrypi:~ $ sudo cp /home/pi/lan_traffic/index.php /var/www/html/index.php
```
`.css`ファイルをダウンロードし，展開．
```
pi@raspberrypi:~ $ wget -P /var/tmp/ https://github.com/ysakasin/Umi/releases/download/v4.0.0/bootstrap-umi-4.0.0-dist.zip
pi@raspberrypi:~ $ sudo unzip /var/tmp/bootstrap-umi-4.0.0-dist.zip -d /var/www/html/
```
LAN内からWebブラウザでRaspberry PiのIPアドレスにアクセス．

[http://192.168.0.3](http://192.168.0.3)


## 参考文献
- https://mugeek.hatenablog.com/entry/2019/05/27/230256
- https://aokakes.hatenablog.com/entry/2020/05/09/194143
- https://deviceplus.jp/hobby/how-to-build-web-server-with-raspberry-pi/