# commentary_backend

## これは何？

mtgatracker_backend、AssistantSeikaと組み合わせてMTG ArenaをVOICEROID等に実況させるためのツールです。
紹介動画（ https://www.nicovideo.jp/watch/sm39704958 ）を見ればおおよそ分かると思います。

## 導入方法

1. AssistantSeikaで利用できる音声合成製品を導入する
2. AssistantSeikaを導入する
3. mtgatracker_backend.zipをダウンロードし、適当なフォルダに展開する
4. commentary_backend.zipをダウンロードし、適当なフォルダに展開する
5. AssistantSeikaに同梱されているSeikaSay2.exeをcommentary_backend.exeと同じフォルダにコピーする

## 起動手順

1. AssistantSeikaで利用できる音声合成製品を起動する
2. AssistantSeikaを起動する
3. AssistantSeikaの製品スキャンを実行し、話者一覧に実況させたい話者が表示されていることを確認する
4. MTG Arenaを起動する
5. mtgatracker_backend.exeを実行する
6. commentary_backend.exeを実行する

commentary_backendの起動後、MTG Arenaをプレイすると、勝手に実況してくれます。
Windows 10 の Xbox Game Barで実況付きで録画する場合、設定/キャプチャ中/録音するオーディオを「すべて」にする必要があります。
その場合、通知音や音声通話等がすべて録音されるのでご注意ください。

## 停止手順

1. mtgatracker_backend.exeを実行した際に表示されるウィンドウを、右上の×ボタンをクリックして閉じてください。
2. mtgatracker_backendを停止すれば、commentary_backendは自動的に停止します。

## より詳しい使い方

https://github.com/poslogithub/binary-dist/blob/main/mtga-commentary-automation/README.md を参照してください。

## 連絡先

https://twitter.com/poslog

## ライセンス

MIT License

Copyright (c) 2021 poslogithub

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

mtgatrackerおよび外部ライブラリのライセンスはLICENSEフォルダを参照してください。
