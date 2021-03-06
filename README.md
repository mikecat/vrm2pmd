vrm2pmd
=======

## 概要

[VRoid Studio](https://studio.vroid.com/)で作れる[VRM形式](https://dwango.github.io/vrm/)のモデルデータを、
[ＤＸライブラリ](https://dxlib.xsrv.jp/index.html)で読み込める[PMD形式](https://blog.goo.ne.jp/torisu_tetosuki/e/209ad341d3ece2b1b4df24abf619d6e4)のモデルデータに変換する。

## ヒント

### PMDの面頂点リストにおける制限の突破

PMDの面頂点リストに書ける頂点番号は65535まで(2バイト)という制約があり、
[ニコニ立体ちゃんのモデル](https://3d.nicovideo.jp/works/td32797)はこれを超えてしまいました。
そこで、1つのモデルに収まった頂点を外し、残りの頂点を別のモデルにする機能を用意しました。

`vrd2pmd.py` の第三引数で、先頭から外す頂点数を指定できます。65535の倍数を指定するといいでしょう。

## ライセンス

TBD

* 個人/法人、商用/非商用を問わず、無料で使用してかまいません。
  ただし、使用した、またはしなかったことにより発生した損害について、一切責任を負いません。
  また、バグや不都合が無い保証はありません。使用する場合は自己責任でお願いします。
* モデルの利用条件に違反しないようにしましょう。
