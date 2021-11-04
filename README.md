# lan_traffic
Raspberry Piを使ってLAN内のトラフィックを監視する．

## 必要なもの
- ポートミラーリング機能のあるスイッチングハブ
- Raspberry Pi
- Raspberry Piでキャプチャした`.pcap`ファイルを保存する外付けHDD

## ネットワーク図
![lan_network](https://raw.githubusercontent.com/FunabikiKeisuke/lan_traffic/main/lan_traffic.drawio.svg)

ここで図中の紫実線は有線LAN，紫破線は無線LANを示す．
スイッチングハブを経由して通信している端末のトラフィックを，スイッチングハブのポートミラーリング機能でRaspberry Piへミーラーリングする．
Wi-Fi ルータは二重ルータを防ぐためにアクセスポイントモードにする必要がある．

## 参考文献
https://aokakes.hatenablog.com/entry/2020/05/09/194143