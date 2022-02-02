# mtga-commentary-automation

MTGATrackerのbackend、およびAssistantSeikaと組み合わせて、VOICEROID等にMTGAの実況をしてもらうためのツールです。<br />
このREADMEには仕様的な内容を記載します。<br />
開発メモは[Wiki](https://github.com/poslogithub/mtga-commentary-automation/wiki)に記載します。<br />
配布バイナリの導入手順と詳細な使い方は[配布用リポジトリ](https://github.com/poslogithub/binary-dist)のREADME.mdを参照してください。<br />

## 実況内容

* 実況するイベント
  * ゲーム開始
  * ゲーム終了
  * マリガンチェック
  * ドロー
  * 土地のプレイ
  * 呪文のキャスト
  * 呪文の解決
  * 攻撃クリーチャー指定
  * ブロッククリーチャー指定
  * 墓地送り
    * 理由によって実況内容を変えられる。
    * 対応済の理由
      * "(Conjure)", (Discard)", "(Destroy)", "(Sacrifice)", "(SBA_Damage)", "(SBA_UnattachedAura)", "(SBA_ZeroToughness)", "(nil)"
        * SBAは状況起因処理（State-Based Action）の略
        * (nil)は立ち消えとか（多分）
    * 未対応の理由（何という理由が送られてくるのか分からないため）
      * レジェンド・ルール
      * 切削
      * その他、上記に記載が無いもの全部
  * カードの追放
    * 追放元の領域は判別できない（MTGATrackerから追放元領域の情報が来ない）ため、墓地掃除や続唱でひどいことになる可能性がある。
  * ライフ変動
    * 増えるか減るかによって実況内容を変えられる。
* 実況しないイベント（該当するメッセージがMTGATrackerから来ないため）
  * マリガン
  * 非パーマネント呪文が解決されたことによる墓地送り
  * パーマネントの着地
  * 起動型能力の起動
  * 誘発型能力の誘発
  * 占術
  * サーチ
  * その他、上記に記載が無いもの全部
