# mtga-commentary-automation

MTGATrackerのbackend、およびAssistantSeikaと組み合わせて、VOICEROID等にMTGAの実況をしてもらうためのツール。
 
## 使い方

### 前提条件

以下がインストール済であること。

* [Python](https://www.python.org/), [pip](https://pypi.org/project/pip/)
* [poslogithub/python-mtga](https://github.com/poslogithub/python-mtga)
  * [set_data/dynamic.py](https://github.com/poslogithub/python-mtga/blob/master/source/mtga/set_data/dynamic.py)の94行目の「en-US」を「ja-JP」に書き換えてください。
* [poslogithub/mtgatracker](https://github.com/poslogithub/mtgatracker)
* [AssistantSeika](https://hgotoh.jp/wiki/doku.php/documents/voiceroid/assistantseika/start)
* [VOICEROID+ 東北きりたん EX](https://www.ah-soft.com/voiceroid/kiritan/)、または[AssistantSeikaが対応している音声合成製品](https://hgotoh.jp/wiki/doku.php/documents/voiceroid/assistantseika/assistantseika-004)
  * 東北きりたん以外を使用する場合は、[poslogithub/mtga-commentary-automation/seikasay2.py](https://github.com/poslogithub/mtga-commentary-automation/blob/main/src/mtgacommentary/seikasay2.py)のcidを書き換える必要があります。

### 導入方法

ZIPをダウンロードして展開してください。<br />
`pip install git+https://github.com/poslogithub/mtga-commentary-automation`でもできるように作ったつもりです（検証してない）。<br />
実行時にモジュールが足りないと言われたら、適宜インストールしてください。<br />
何を言っているのか分からないという人は、諦めてください。<br />

### 使用方法

1. MTGAを起動する。
2. 東北きりたんを起動する。
3. AssistantSeikaを起動する。
4. AssistantSeikaで製品スキャンを行い、話者一覧に東北きりたんが表示されることを確認する。
5. [poslogithub/mtgatracker/app/mtgatracker_backend.py](https://github.com/poslogithub/mtgatracker/blob/master/app/mtgatracker_backend.py)を起動する。
6. [poslogithub/mtga-commentary-automation/commentary_backend.py](https://github.com/poslogithub/mtga-commentary-automation/blob/main/src/mtgacommentary/commentary_backend.py)を起動する。
7. MTGAをプレイする。

MTGA→mtgatracker_backend.py→commentary_backend.pyの起動順序は守ってください。

## 今後やりたいこと

* 実況するイベントを増やす（何が氏んだとか何が誘発したとか）。
  * websocketで送信するメッセージを正規のJSONにする。
* MTGA→mtgatracker_backend.py→commentary_backend.pyの起動順序を守らなくてもいいようにする。
* 実況する内容やcidを設定ファイルに外出しする。
* 導入方法を簡単にする。
