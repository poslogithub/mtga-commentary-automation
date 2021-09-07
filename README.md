# mtga-commentary-automation

MTGATrackerのbackend、およびAssistantSeikaと組み合わせて、VOICEROID等にMTGAの実況をしてもらうためのツールです。
 
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

# 実況内容

## 実況するイベント

* ゲーム開始
* ゲーム終了
* マリガンチェック
* 自分のドロー
* 土地のプレイ
* 呪文のキャスト
* 攻撃クリーチャー指定
* ブロッククリーチャー指定
* 墓地送り
  * 理由によって実況内容が変わる。
  * 非パーマネント呪文の解決による墓地送りは実況しない（MTGATrackerからメッセージが来ないため）。
* カードの追放
  * 追放元の領域は問わない（MTGATrackerから追放元領域の情報が来ないため）。<br />そのため、墓地掃除とか食らったらひどいことになる可能性がある。少なくとも脱出コストの支払いによる追放は実況する。
* ライフ変動

## 実況しないイベント

* 該当するメッセージがMTGATrackerから来ないため
  * マリガン
  * 非パーマネント呪文が解決されたことによる墓地送り
  * 起動型能力の起動（実況したい）
  * 誘発型能力の誘発
  * 占術（実況したい）
  * サーチ（実況したい）
* 不要と判断したため
  * 対戦相手のドロー
  * 呪文の解決
  * 能力の解決

## 未確認のイベント

* 切削による墓地送り
* 予顕による追放

# 今後やりたいこと

* mtgatracker_backendとcommentary_backendをexe化する。
* MTGA→mtgatracker_backend→commentary_backendの起動順序を守らなくてもいいようにする。
  * commentary_backend起動時に、MTGA, AssistantSeika（話者一覧が空でないか含む。`-list`オプションで実現可...のはず）, mtgatracker_backendが起動チェックを行う。
  * VOICEROIDの起動チェックと、話者一覧とcommentary_backendが認識しているcidが一致しているかの確認まではしない。勘弁して。
* 実況する内容やcidを設定ファイルに外出しする。
* 自分と対戦相手で話者を変えられるようにする。
