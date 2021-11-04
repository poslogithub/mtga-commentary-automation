import _thread
from enum import Enum
import json
import logging
import logging.handlers
import os
import re
import sys
import tkinter
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
import psutil
import websocket

from seikasay2 import SeikaSay2


# message from mtgatracker_backend
class MessageKey:
    GAME_HISTORY_EVENT = "game_history_event"
    TYPE = "type"
    TEXT = "text"

class MessageValue:
    GAME = "game"
    TURN = "turn"
    HERO = "hero"
    OPPONENT = "opponent"

class Verb:
    ATTAKING = "attacking"
    BLOCKS = "blocks"
    CASTS = "casts"
    COUNTERS = "counters"
    DRAWS = "draws"
    EXILES = "exiles"
    LIFE_TOTAL_CHANGED = "'s life total changed"
    PLAYS = "plays"
    RESOLVES = "resolves"
    SENT_TO_GRAVEYARD = "sent to graveyard"
    STARTING_HAND = "'s starting hand:"
    VS = "vs"

class Reason(Enum):
    # message from mtgatracker_backend
    CONJURE = "(Conjure)"
    DESTROY = "(Destroy)"
    DISCARD = "(Discard)"
    MILL = "(Mill)"
    PUT = "(Put)"
    SACRIFICE = "(Sacrifice)"
    SBA_DAMEGE = "(SBA_Damage)"
    SBA_DEATHTOUCH = "(SBA_Deathtouch)",
    SBA_ZERO_TOUGHNESS = "(SBA_ZeroToughness)"
    SBA_UNATTACHED_AURA = "(SBA_UnattachedAura)"
    NIL = "(nil)"


class ParseKey:
    IS_OPPONENT = "isOpponent"
    MESSAGE_TYPE = "messageType"
    VERB = "verb"
    ATTACKER = "attacker"
    BLOCKER = "blocker"
    CARD = "card"
    SOURCE = "source"
    TARGET = "target"
    REASON = "reason"
    LIFE_FROM = "life_from"
    LIFE_TO = "life_to"
    LIFE_DIFF = "life_diff"

class ReplaceWord(Enum):
    ATTACKER = ParseKey.ATTACKER
    BLOCKER = ParseKey.BLOCKER
    CARD = ParseKey.CARD
    SOURCE = ParseKey.SOURCE
    TARGET = ParseKey.TARGET
    LIFE_FROM = ParseKey.LIFE_FROM
    LIFE_TO = ParseKey.LIFE_TO
    LIFE_DIFF = ParseKey.LIFE_DIFF


class ConfigKey:
    SEIKA_SAY2_PATH = "seikaSay2Path"
    SPEAKER1 = "speaker1"
    SPEAKER2 = "speaker2"
    CID = "cid"
    NAME = "name"
    HERO_COMMENTARY_TYPE = "heroCommentaryType"
    OPPONENT_COMMENTARY_TYPE = "opponentCommentaryType"
    MTGATRACKER_BACKEND_URL = "mtgatrackerBackendUrl"

class ConfigValue:
    SPEAKER1 = "speaker1"
    SPEAKER2 = "speaker2"
    NEVER = "never"


class SpeakerKey:
    LIFE = "life"
    SPEAK = "speak"
    TEXT = MessageKey.TEXT
    TYPE = MessageKey.TYPE
    EVENT = "event"

class SpeakerValue:
    SEIKA_SAY2 = "seikaSay2"
    GAIN = "gain"
    LOSE = "lose"

class SpeakerParamKey:
    ASYNC = "async"
    VOLUME = "volume"
    SPEED = "speed"
    PITCH = "pitch"
    ALPHA = "alpha"
    INTONATION = "intonation"
    EMOTION_EP = "emotionEP"
    EMOTION_P = "emotionP"
    OVER_BANNER = "overBanner"


class SpeakerLabel:
    GAME_START = "ゲーム開始時"
    GAME_WIN = "ゲーム勝利時"
    GAME_LOSE = "ゲーム敗北時"
    MULLIGAN_CHECK = "マリガンチェック時"
    TURN_START = "ターン開始時"
    DRAW = "カードを引いた時"
    DISCARD = "カードを捨てた時"
    PLAY_LAND = "土地をプレイした時"
    CAST_SPELL = "呪文を唱えた時"
    COUNTERED = "呪文が打ち消された時"
    RESOLVE = "呪文が解決した時"
    EXILE = "カードが追放された時"
    CONJURE = "墓地にカードが置かれた時（創出）"
    DESTROY = "墓地にカードが置かれた時（破壊）"
    MILL = "墓地にカードが置かれた時（切削）"
    PUT = "墓地にカードが置かれた時（効果）"
    SACRIFICE = "墓地にカードが置かれた時（生け贄）"
    DIE = "墓地にカードが置かれた時（死亡）"
    UNATTACHED_AURA = "墓地にカードが置かれた時（不正オーラ）"
    NIL = "墓地にカードが置かれた時（対象不適正）"
    ATTACK = "攻撃クリーチャー指定時"
    BLOCK = "ブロッククリーチャー指定時"
    LIFE_GAIN = "ライフが増えた時"
    LIFE_LOSE = "ライフが減った時"

class Event:
    GAME_START = "gameStart"
    GAME_WIN = "gameWin"
    GAME_LOSE = "gameLose"
    MULLIGAN_CHECK = "MulliganCheck"
    TURN_START = "TurnStart"
    DRAW = "Draw"
    DISCARD = "Discard"
    PLAY_LAND = "PlayLand"
    CAST_SPELL = "CastSpell"
    COUNTERED = "Countered"
    RESOLVE = "Resolve"
    EXILE = "Exile"
    CONJURE = "Conjure"
    DESTROY = "Destroy"
    MILL = "Mill"
    PUT = "Put"
    SACRIFICE = "Sacrifice"
    DIE = "Die"
    UNATTACHED_AURA = "UnattachedAura"
    NIL = "nil"
    ATTACK = "Attack"
    BLOCK = "Block"
    LIFE_GAIN = "LifeGain"
    LIFE_LOSE = "LifeLose"

class SpeakerWindowEntry(Enum):
    # (キー名, ラベルtext, textvariable)
    GAME_START = (Event.GAME_START, "ゲーム開始時")
    GAME_WIN = (Event.GAME_WIN, "ゲーム勝利時")
    GAME_LOSE = (Event.GAME_LOSE, "ゲーム敗北時")
    MULLIGAN_CHECK = (Event.MULLIGAN_CHECK, "マリガンチェック時")
    TURN_START = (Event.TURN_START, "ターン開始時")
    DRAW = (Event.DRAW, "カードを引いた時")
    DISCARD = (Event.DISCARD, "カードを捨てた時")
    PLAY_LAND = (Event.PLAY_LAND, "土地をプレイした時")
    CAST_SPELL = (Event.CAST_SPELL, "呪文を唱えた時")
    COUNTERED = (Event.COUNTERED, "呪文が打ち消された時")
    RESOLVE = (Event.RESOLVE, "呪文が解決された時")
    ATTACK = (Event.ATTACK, "攻撃クリーチャー指定時")
    BLOCK = (Event.BLOCK, "ブロッククリーチャー指定時")
    LIFE_GAIN = (Event.LIFE_GAIN, "ライフが増えた時")
    LIFE_LOSE = (Event.LIFE_LOSE, "ライフが減った時")
    EXILE = (Event.EXILE, "カードが追放された時")
    DIE = (Event.DIE, "墓地にカードが置かれた時（死亡）")
    DESTROY = (Event.DESTROY, "墓地にカードが置かれた時（破壊）")
    SACRIFICE = (Event.SACRIFICE, "墓地にカードが置かれた時（生け贄）")
    MILL = (Event.MILL, "墓地にカードが置かれた時（切削）")
    PUT = (Event.PUT, "墓地にカードが置かれた時（効果）")
    NIL = (Event.NIL, "墓地にカードが置かれた時（対象不適正）")
    UNATTACHED_AURA = (Event.UNATTACHED_AURA, "墓地にカードが置かれた時（不正オーラ）")
    CONJURE = (Event.CONJURE, "墓地にカードが創出された時")


class ProcessName:
    ASSISTANT_SEIKA = "AssistantSeika.exe"
    MTGATRACKER_BACKEND = "mtgatracker_backend.exe"
    SEIKA_SAY2 = "SeikaSay2.exe"


class CommentaryBackend(tkinter.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        # 定数
        self.CONFIG_FILE = "config\\config.json"
        self.DEFAULT_SPEAKER_FILE = "config\\defaultSpeaker.json"
        self.LOG_FILE = os.path.basename(__file__).split(".")[0]+".log"

        # 変数
        self.config = {
            ConfigKey.SEIKA_SAY2_PATH : ".\\"+ProcessName.SEIKA_SAY2,
            ConfigKey.SPEAKER1 : {
                ConfigKey.CID : 0,
                ConfigKey.NAME : ""
            },
            ConfigKey.SPEAKER2 : {
                ConfigKey.CID : 0,
                ConfigKey.NAME : ""
            },
            ConfigKey.HERO_COMMENTARY_TYPE : ConfigValue.SPEAKER1,
            ConfigKey.OPPONENT_COMMENTARY_TYPE : ConfigValue.SPEAKER1,
            ConfigKey.MTGATRACKER_BACKEND_URL : "ws://localhost:8089"
        }
        self.cids = []
        self.speakers = []
        self.speaker1_obj = {}
        self.speaker2_obj = {}
        self.hero_screen_name = ""
        self.opponent_screen_name = ""
        self.HERO_COMMENTARY_TYPES = ["話者1が一人称で実況する", "実況しない"]
        self.OPPONENT_COMMENTARY_TYPES = ["話者1が三人称で実況する", "話者2が一人称で実況する", "実況しない"]

        # GUI
        self.master.title("MTGA自動実況ツール")
        self.master.geometry("600x360")
        self.master_frame = tkinter.Frame(self.master)
        self.master_frame.pack()
        self.master_text = ScrolledText(self.master_frame)
        self.master_text.pack()
        self.master_quit = tkinter.Button(self.master_frame, text="終了", command=self.master_frame_quit)
        self.master_quit.pack()

        # logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.INFO)
        must_rollover = False
        if os.path.exists(self.LOG_FILE):  # check before creating the handler, which creates the file
            must_rollover = True
        rotating_handler = logging.handlers.RotatingFileHandler(self.LOG_FILE, backupCount=10)
        rotating_handler.setLevel(logging.DEBUG)
        if must_rollover:
            try:
                rotating_handler.doRollover()
            except PermissionError:
                print("警告: {} のローテーションに失敗しました。ログファイルが出力されません。".format(self.LOG_FILE))
        self.logger.addHandler(stream_handler)
        self.logger.addHandler(rotating_handler)

        # load config
        self.logger.info("Loading {}".format(self.CONFIG_FILE))
        if self.load_config():
            self.logger.info("Loading {}: OK".format(self.CONFIG_FILE))
        else:
            self.logger.info("Loading {}: NG".format(self.CONFIG_FILE))
        self.seikasay2 = SeikaSay2(self.config.get(ConfigKey.SEIKA_SAY2_PATH))

    def master_frame_quit(self):
        self.master.destroy()

    def start_ws_client(self):
        import threading
        t = threading.Thread(target=self.connect_to_socket)
        t.start()        

    def connect_to_socket(self):
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp(self.config.get(ConfigKey.MTGATRACKER_BACKEND_URL),
            on_open = self.on_open,
            on_message = self.on_message,
            on_error = self.on_error,
            on_close = self.on_close)
        self.ws.run_forever()

    def load_config(self, config_file=None):
        if not config_file:
            config_file = self.CONFIG_FILE
        if not os.path.exists(config_file):
            self.save_config(config_file, self.config)
        with open(config_file if config_file else self.CONFIG_FILE, 'r', encoding="utf_8_sig") as rf:
            self.config = json.load(rf)
        return self.config
    
    def save_config(self, config_file=None, config=None):
        with open(config_file if config_file else self.CONFIG_FILE, 'w', encoding="utf_8_sig") as wf:
            json.dump(config if config else self.config, wf, indent=4, ensure_ascii=False)
    
    def open_config_window(self):
        speaker1_index = self.cids.index(self.config.get(ConfigKey.SPEAKER1).get(ConfigKey.CID))
        speaker2_index = self.cids.index(self.config.get(ConfigKey.SPEAKER2).get(ConfigKey.CID))
        self.logger.debug("open_config_window")
        self.config_window = tkinter.Toplevel(self)
        self.config_window.title("MTGA自動実況ツール - 設定ウィンドウ")
        self.config_window.geometry("520x220")
        self.config_window.grab_set()   # モーダルにする
        self.config_window.focus_set()  # フォーカスを新しいウィンドウをへ移す
        self.config_window.transient(self.master)   # タスクバーに表示しない
        self.config_frame = ttk.Frame(self.config_window)
        self.config_frame.grid(column=0, row=0, sticky=tkinter.NSEW, padx=5, pady=10)
        self.sv_seikasay2_path = tkinter.StringVar()
        self.sv_seikasay2_path.set(self.config.get(ConfigKey.SEIKA_SAY2_PATH))
        self.sv_speaker1 = tkinter.StringVar()
        self.sv_speaker2 = tkinter.StringVar()
        self.sv_hero_commentary_type = tkinter.StringVar()
        self.sv_opponent_commentary_type = tkinter.StringVar()
        label_seikasay2 = ttk.Label(self.config_frame, text="SeikaSay2のパス: ", anchor="w")
        label_seikasay2.grid(row=0, column=0, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        entry_seikasay2 = ttk.Entry(self.config_frame, width=40, textvariable=self.sv_seikasay2_path)
        entry_seikasay2.grid(row=0, column=1, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        button_seikasay2 = tkinter.Button(self.config_frame, text="参照", command=self.config_window_seikasay2)
        button_seikasay2.grid(row=0, column=2, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        label_speaker1 = ttk.Label(self.config_frame, text="話者1: ", anchor="w")
        label_speaker1.grid(row=1, column=0, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        combobox_speaker1 = ttk.Combobox(self.config_frame, width=40, values=self.speakers, textvariable=self.sv_speaker1, state="readonly")
        combobox_speaker1.current(speaker1_index)
        combobox_speaker1.grid(row=1, column=1, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        label_speaker2 = ttk.Label(self.config_frame, text="話者2: ", anchor="w")
        label_speaker2.grid(row=2, column=0, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        combobox_speaker2 = ttk.Combobox(self.config_frame, width=40, values=self.speakers, textvariable=self.sv_speaker2, state="readonly")
        combobox_speaker2.current(speaker2_index)
        combobox_speaker2.grid(row=2, column=1, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        label_hero_commentary_type = ttk.Label(self.config_frame, text="自分のアクション: ", anchor="w")
        label_hero_commentary_type.grid(row=3, column=0, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        combobox_hero_commentary_type = ttk.Combobox(self.config_frame, width=40, values=self.HERO_COMMENTARY_TYPES, textvariable=self.sv_hero_commentary_type, state="readonly")
        combobox_hero_commentary_type.current(0 if self.config.get(ConfigKey.HERO_COMMENTARY_TYPE) == ConfigValue.SPEAKER1 else 1)
        combobox_hero_commentary_type.grid(row=3, column=1, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        label_opponent_commentary_type = ttk.Label(self.config_frame, text="対戦相手のアクション: ", anchor="w")
        label_opponent_commentary_type.grid(row=4, column=0, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        combobox_opponent_commentary_type = ttk.Combobox(self.config_frame, width=40, values=self.OPPONENT_COMMENTARY_TYPES, textvariable=self.sv_opponent_commentary_type, state="readonly")
        combobox_opponent_commentary_type.current(0 if self.config.get(ConfigKey.OPPONENT_COMMENTARY_TYPE) == ConfigValue.SPEAKER1 else 1 if self.config.get(ConfigKey.OPPONENT_COMMENTARY_TYPE) == ConfigValue.SPEAKER2 else 2)
        combobox_opponent_commentary_type.grid(row=4, column=1, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        button_ok = tkinter.Button(self.config_frame, text="保存して開始", command=self.config_window_ok)
        button_ok.grid(row=5, column=1, sticky=tkinter.E, padx=5, pady=5)
        button_cancel = tkinter.Button(self.config_frame, text="保存しないで開始", command=self.config_window_cancel)
        button_cancel.grid(row=5, column=2, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        self.wait_window(self.config_window)
    
    def config_window_seikasay2(self):
        path = filedialog.askopenfilename(filetype=[("実行ファイル","*.exe")], initialdir=os.getcwd())
        self.sv_seikasay2_path.set(path)

    def config_window_ok(self):
        self.config[ConfigKey.SEIKA_SAY2_PATH] = self.sv_seikasay2_path.get()
        self.config[ConfigKey.SPEAKER1][ConfigKey.CID] = self.sv_speaker1.get().split(" ")[0]
        self.config[ConfigKey.SPEAKER1][ConfigKey.NAME] = self.sv_speaker1.get()
        self.config[ConfigKey.SPEAKER2][ConfigKey.CID] = self.sv_speaker2.get().split(" ")[0]
        self.config[ConfigKey.SPEAKER2][ConfigKey.NAME] = self.sv_speaker2.get()
        self.config[ConfigKey.HERO_COMMENTARY_TYPE] = \
            ConfigValue.SPEAKER1 if self.sv_hero_commentary_type.get() == self.HERO_COMMENTARY_TYPES[0] \
            else ConfigValue.NEVER
        self.config[ConfigKey.OPPONENT_COMMENTARY_TYPE] = \
            ConfigValue.SPEAKER1 if self.sv_opponent_commentary_type.get() == self.OPPONENT_COMMENTARY_TYPES[0] \
            else ConfigValue.SPEAKER2 if self.sv_opponent_commentary_type.get() == self.OPPONENT_COMMENTARY_TYPES[1] \
            else ConfigValue.NEVER
        self.save_config()
        self.config_window.destroy()

    def config_window_cancel(self):
        self.config_window.destroy()

    def open_speaker1_window(self):
        self.open_speaker_window(self.sv_speaker1.get().split(" ")[0])

    def open_speaker2_window(self):
        self.open_speaker_window(self.sv_speaker2.get().split(" ")[0])
        
    def open_speaker_window(self, cid):
        speaker = self.load_speaker(cid)
        self.logger.debug("open_speaker_window")
        self.speaker_window = tkinter.Toplevel(self.config_window)
        self.speaker_window.title("MTGA自動実況ツール - 話者ウィンドウ")
        self.speaker_window.geometry("480x260")
        self.speaker_window.grab_set()   # モーダルにする
        self.speaker_window.focus_set()  # フォーカスを新しいウィンドウをへ移す
        self.speaker_window.transient(self.master)   # タスクバーに表示しない
        self.speaker_frame = ttk.Frame(self.speaker_window)
        self.speaker_frame.grid(column=0, row=0, sticky=tkinter.NSEW, padx=5, pady=10)
        #TODO for key in Timing.SPEAKER_TUPLE
        labels = {}
        for key in Label.SPEAKER_LIST:
            labels[key] = ttk.Label(self.speaker_frame, text=key, anchor="w")

        self.sv[Timing.GAME_START] = tkinter.StringVar()
        self.sv_seikasay2_path.set(self.speaker.get(Key.SEIKA_SAY2_PATH))
        label_game_start = ttk.Label(self.speaker_frame, text=Label.GAME_START, anchor="w")
        label_game_start.grid(row=0, column=0, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        entry_game_start = ttk.Entry(self.speaker_frame, width=40, textvariable=self.sv_seikasay2_path)
        entry_game_start.grid(row=0, column=1, sticky=tkinter.W + tkinter.E, padx=5, pady=5)


        self.sv_seikasay2_path = tkinter.StringVar()
        self.sv_seikasay2_path.set(self.speaker.get(Key.SEIKA_SAY2_PATH))
        self.sv_speaker1 = tkinter.StringVar()
        self.sv_speaker2 = tkinter.StringVar()
        self.sv_hero_commentary_type = tkinter.StringVar()
        self.sv_opponent_commentary_type = tkinter.StringVar()
        label_seikasay2 = ttk.Label(self.speaker_frame, text="SeikaSay2のパス: ", anchor="w")
        label_seikasay2.grid(row=0, column=0, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        entry_seikasay2 = ttk.Entry(self.speaker_frame, width=40, textvariable=self.sv_seikasay2_path)
        entry_seikasay2.grid(row=0, column=1, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        button_seikasay2 = tkinter.Button(self.speaker_frame, text="参照", command=self.speaker_window_seikasay2)
        button_seikasay2.grid(row=0, column=2, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        label_speaker1 = ttk.Label(self.speaker_frame, text="話者1: ", anchor="w")
        label_speaker1.grid(row=1, column=0, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        combobox_speaker1 = ttk.Combobox(self.speaker_frame, width=40, values=self.speakers, textvariable=self.sv_speaker1, state="readonly")
        combobox_speaker1.current(speaker1_index)
        combobox_speaker1.grid(row=1, column=1, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        label_speaker2 = ttk.Label(self.speaker_frame, text="話者2: ", anchor="w")
        label_speaker2.grid(row=2, column=0, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        combobox_speaker2 = ttk.Combobox(self.speaker_frame, width=40, values=self.speakers, textvariable=self.sv_speaker2, state="readonly")
        combobox_speaker2.current(speaker2_index)
        combobox_speaker2.grid(row=2, column=1, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        label_hero_commentary_type = ttk.Label(self.speaker_frame, text="自分のアクション: ", anchor="w")
        label_hero_commentary_type.grid(row=3, column=0, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        combobox_hero_commentary_type = ttk.Combobox(self.speaker_frame, width=40, values=self.HERO_COMMENTARY_TYPES, textvariable=self.sv_hero_commentary_type, state="readonly")
        combobox_hero_commentary_type.current(0 if self.speaker.get(Key.HERO_COMMENTARY_TYPE) == Value.SPEAKER1 else 1)
        combobox_hero_commentary_type.grid(row=3, column=1, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        label_opponent_commentary_type = ttk.Label(self.speaker_frame, text="対戦相手のアクション: ", anchor="w")
        label_opponent_commentary_type.grid(row=4, column=0, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        combobox_opponent_commentary_type = ttk.Combobox(self.speaker_frame, width=40, values=self.OPPONENT_COMMENTARY_TYPES, textvariable=self.sv_opponent_commentary_type, state="readonly")
        combobox_opponent_commentary_type.current(0 if self.speaker.get(Key.OPPONENT_COMMENTARY_TYPE) == Value.SPEAKER1 else 1 if self.speaker.get(Key.OPPONENT_COMMENTARY_TYPE) == Value.SPEAKER2 else 2)
        combobox_opponent_commentary_type.grid(row=4, column=1, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        button_ok = tkinter.Button(self.speaker_frame, text="保存して開始", command=self.speaker_window_ok)
        button_ok.grid(row=5, column=1, sticky=tkinter.E, padx=5, pady=5)
        button_cancel = tkinter.Button(self.speaker_frame, text="保存しないで開始", command=self.speaker_window_cancel)
        button_cancel.grid(row=5, column=2, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        self.wait_window(self.speaker_window)

    def load_speaker(self, cid):
        speaker_file = "config\\{}.json".format(cid)
        if not os.path.isfile(speaker_file):
            speaker_file = self.DEFAULT_SPEAKER_FILE
        with open(speaker_file, 'r', encoding="utf_8_sig") as rf:
            return json.load(rf)

    def load_speakers(self):
        speaker_file = "config\\{}.json".format(self.config.get(ConfigKey.SPEAKER1).get(ConfigKey.CID))
        if not os.path.isfile(speaker_file):
            speaker_file = self.DEFAULT_SPEAKER_FILE
        with open(speaker_file, 'r', encoding="utf_8_sig") as rf:
            self.speaker1_obj = json.load(rf)

        speaker_file = "config\\{}.json".format(self.config.get(ConfigKey.SPEAKER2).get(ConfigKey.CID))
        if not os.path.isfile(speaker_file):
            speaker_file = self.DEFAULT_SPEAKER_FILE
        with open(speaker_file, 'r', encoding="utf_8_sig") as rf:
            self.speaker2_obj = json.load(rf)

    def save_speaker(self, cid, speaker):
        speaker_file = "config\\{}.json".format(cid)
        with open(speaker_file, 'w', encoding="utf_8_sig") as wf:
            json.dump(speaker, wf, ensure_ascii=False)
    
    def del_ruby(self, s):
        return re.sub("（.+?）", "", s)

    def parse(self, blob):
        self.logger.debug(blob)
        if blob:
            text_array = blob.get(MessageKey.GAME_HISTORY_EVENT)
            if not text_array:
                return None
            parsed = {}

            if len(text_array) == 0:
                self.logger.warning("warning: 長さ0のtext_array")
            elif len(text_array) == 1:
                if text_array[0].get(MessageKey.TYPE) == MessageValue.GAME:
                    parsed[ParseKey.MESSAGE_TYPE] = text_array[0].get(MessageKey.TYPE)
                elif text_array[0].get(MessageKey.TYPE) == MessageValue.TURN:
                    if text_array[0].get(MessageKey.TEXT).find(self.opponent_screen_name) >= 0:
                        parsed[ParseKey.IS_OPPONENT] = True
                    parsed[ParseKey.MESSAGE_TYPE] = text_array[0].get(MessageKey.TYPE)
                else:
                    self.logger.warning("warning: 不明なtype: {}".format(text_array[0].get(MessageKey.TYPE)))
            else:
                parsed[ParseKey.VERB] = text_array[1].strip()
                if parsed.get(ParseKey.VERB) == "'s":    # "'s"が入った場合はガチャガチャする
                    parsed[ParseKey.SOURCE] = text_array[0].get(MessageKey.TEXT)
                    parsed[ParseKey.IS_OPPONENT] = True if text_array[0].get(MessageKey.TYPE) == MessageValue.OPPONENT else False
                    parsed[ParseKey.MESSAGE_TYPE] = text_array[2].get(MessageKey.TYPE)    # ability
                    if len(text_array) >= 4 and text_array[3].strip() != ":":   # ex: "CARDNAME1 's ability exiles CARDNAME2"
                        text_array = text_array[2:]
                    elif len(text_array) >= 6 and text_array[3].strip() == ":": # ex: "CARDNAME1 's ability : SCREENNAME draws CARDNAME2"
                        text_array = text_array[4:]
                    parsed[ParseKey.VERB] = text_array[1].strip()
                    if parsed.get(ParseKey.VERB) == "'s":
                        self.logger.warning("warning: 不明なtext_array: {}".format(text_array))

                if parsed.get(ParseKey.VERB) == ":":    # ":"が入った場合はガチャガチャする
                    parsed[ParseKey.SOURCE] = text_array[0].get(MessageKey.TEXT)
                    if len(text_array) >= 4:   # ex: "CARDNAME1 : SCREENNAME draws CARDNAME2"
                        text_array = text_array[2:]
                    parsed[ParseKey.VERB] = text_array[1].strip()
                    if parsed.get(ParseKey.VERB) == ":":
                        self.logger.warning("warning: 不明なtext_array: {}".format(text_array))

                if parsed.get(ParseKey.VERB) == Verb.ATTAKING:
                    parsed[ParseKey.IS_OPPONENT] = True if text_array[0].get(MessageKey.TYPE) == MessageValue.OPPONENT else False
                    parsed[ParseKey.ATTACKER] = self.del_ruby(text_array[0].get(MessageKey.TEXT))
                elif parsed.get(ParseKey.VERB) == Verb.BLOCKS:
                    parsed[ParseKey.IS_OPPONENT] = True if text_array[0].get(MessageKey.TYPE) == MessageValue.OPPONENT else False
                    parsed[ParseKey.BLOCKER] = self.del_ruby(text_array[0].get(MessageKey.TEXT))
                    parsed[ParseKey.ATTACKER] = self.del_ruby(text_array[2].get(MessageKey.TEXT))
                elif parsed.get(ParseKey.VERB) == Verb.CASTS:
                    parsed[ParseKey.IS_OPPONENT] = True if text_array[0].get(MessageKey.TYPE) == MessageValue.OPPONENT else False
                    parsed[ParseKey.CARD] = self.del_ruby(text_array[2].get(MessageKey.TEXT))
                elif parsed.get(ParseKey.VERB) == Verb.COUNTERS:
                    parsed[ParseKey.IS_OPPONENT] = True if text_array[0].get(MessageKey.TYPE) == MessageValue.OPPONENT else False
                    parsed[ParseKey.SOURCE] = self.del_ruby(text_array[0].get(MessageKey.TEXT))
                    parsed[ParseKey.TARGET] = self.del_ruby(text_array[2].get(MessageKey.TEXT))
                elif parsed.get(ParseKey.VERB) == Verb.DRAWS:
                    parsed[ParseKey.IS_OPPONENT] = True if text_array[0].get(MessageKey.TYPE) == MessageValue.OPPONENT else False
                    if len(text_array) >= 3:
                        parsed[ParseKey.CARD] = self.del_ruby(text_array[2].get(MessageKey.TEXT))
                elif parsed.get(ParseKey.VERB) == Verb.EXILES:
                    parsed[ParseKey.IS_OPPONENT] = True if text_array[2].get(MessageKey.TYPE) == MessageValue.OPPONENT else False
                    parsed[ParseKey.CARD] = self.del_ruby(text_array[2].get(MessageKey.TEXT))
                elif parsed.get(ParseKey.VERB) == Verb.LIFE_TOTAL_CHANGED:
                    parsed[ParseKey.IS_OPPONENT] = True if text_array[0].get(MessageKey.TYPE) == MessageValue.OPPONENT else False
                    parsed[ParseKey.LIFE_FROM] = int(text_array[2].split(" -> ")[0])
                    parsed[ParseKey.LIFE_TO] = int(text_array[2].split(" -> ")[1])
                    parsed[ParseKey.LIFE_DIFF] = parsed[ParseKey.LIFE_TO] - parsed[ParseKey.LIFE_FROM]
                elif parsed.get(ParseKey.VERB) == Verb.PLAYS:
                    parsed[ParseKey.IS_OPPONENT] = True if text_array[0].get(MessageKey.TYPE) == MessageValue.OPPONENT else False
                    parsed[ParseKey.CARD] = self.del_ruby(text_array[2].get(MessageKey.TEXT))
                elif parsed.get(ParseKey.VERB) == Verb.RESOLVES:
                    parsed[ParseKey.IS_OPPONENT] = True if text_array[0].get(MessageKey.TYPE) == MessageValue.OPPONENT else False
                    parsed[ParseKey.CARD] = self.del_ruby(text_array[0].get(MessageKey.TEXT))
                elif parsed.get(ParseKey.VERB) == Verb.SENT_TO_GRAVEYARD:
                    parsed[ParseKey.IS_OPPONENT] = True if text_array[0].get(MessageKey.TYPE) == MessageValue.OPPONENT else False
                    parsed[ParseKey.CARD] = self.del_ruby(text_array[0].get(MessageKey.TEXT))
                    parsed[ParseKey.REASON] = text_array[2]
                    if parsed.get(ParseKey.REASON) not in [e.value for e in Reason]:
                        self.logger.warning("warning: 不明なreason: {}".format(parsed.get(ParseKey.REASON)))
                elif parsed.get(ParseKey.VERB) == Verb.STARTING_HAND:
                    pass
                elif parsed.get(ParseKey.VERB) == Verb.VS:
                    self.hero_screen_name = text_array[0].get(MessageKey.TEXT)
                    self.opponent_screen_name = text_array[2].get(MessageKey.TEXT)
                else:
                    self.logger.warning("warning: 不明なverb: ".format(parsed.get(ParseKey.VERB)))

            return parsed
        else:
            return None

    def gen_text(self, parsed):
        if not parsed.get(ParseKey.IS_OPPONENT):
            if self.config.get(ConfigKey.HERO_COMMENTARY_TYPE) == ConfigValue.SPEAKER1:
                cid = self.config.get(ConfigKey.SPEAKER1).get(ConfigKey.CID)
                speaker = self.speaker1_obj
                speak_idx = 0
            else:
                return None
        else:
            if self.config.get(ConfigKey.OPPONENT_COMMENTARY_TYPE) == ConfigValue.SPEAKER1:
                cid = self.config.get(ConfigKey.SPEAKER1).get(ConfigKey.CID)
                speaker = self.speaker1_obj
                speak_idx = 1
            elif self.config.get(ConfigKey.OPPONENT_COMMENTARY_TYPE) == ConfigValue.SPEAKER2:
                cid = self.config.get(ConfigKey.SPEAKER2).get(ConfigKey.CID)
                speaker = self.speaker2_obj
                speak_idx = 2
            else:
                return None
        
        speak_obj = None
        if parsed.get(ParseKey.MESSAGE_TYPE) in [MessageValue.GAME, MessageValue.TURN]:
            for obj in speaker:
                if obj.get(MessageKey.TYPE) == parsed.get(ParseKey.MESSAGE_TYPE):
                    speak_obj = obj.get(SpeakerKey.SPEAK)[speak_idx]
                    break
        else:
            for obj in speaker:
                if obj.get(ParseKey.VERB) == parsed.get(ParseKey.VERB):
                    if obj.get(ParseKey.VERB) == Verb.SENT_TO_GRAVEYARD:
                        if parsed.get(ParseKey.REASON) not in obj.get(ParseKey.REASON):
                            continue
                    if obj.get(ParseKey.VERB) == Verb.LIFE_TOTAL_CHANGED:
                        if obj.get(SpeakerKey.LIFE) == SpeakerValue.GAIN and parsed.get(ParseKey.LIFE_DIFF) < 0:
                            continue
                        if obj.get(SpeakerKey.LIFE) == SpeakerValue.LOSE and parsed.get(ParseKey.LIFE_DIFF) > 0:
                            continue
                        parsed[ParseKey.LIFE_DIFF] = abs(parsed.get(ParseKey.LIFE_DIFF))
                    speak_obj = obj.get(SpeakerKey.SPEAK)[speak_idx]
                    break
        
        text = speak_obj.get(SpeakerKey.TEXT)
        for word in ReplaceWord:
            text = text.replace("{"+word.value+"}", str(parsed.get(word.value)) if str(parsed.get(word.value)) else "")

        speak_param_obj = {}
        for obj in speaker:
            if obj.get(SpeakerKey.TYPE) == SpeakerValue.SEIKA_SAY2:
                speak_param_obj = obj
                break
        if not speak_param_obj:
            speak_param_obj[SpeakerParamKey.ASYNC] = speak_obj.get(SpeakerParamKey.ASYNC) if speak_obj.get(SpeakerParamKey.ASYNC) else speak_param_obj.get(SpeakerParamKey.ASYNC)
            speak_param_obj[SpeakerParamKey.VOLUME] = speak_obj.get(SpeakerParamKey.VOLUME) if speak_obj.get(SpeakerParamKey.VOLUME) else speak_param_obj.get(SpeakerParamKey.VOLUME)
            speak_param_obj[SpeakerParamKey.SPEED] = speak_obj.get(SpeakerParamKey.SPEED) if speak_obj.get(SpeakerParamKey.SPEED) else speak_param_obj.get(SpeakerParamKey.SPEED)
            speak_param_obj[SpeakerParamKey.PITCH] = speak_obj.get(SpeakerParamKey.PITCH) if speak_obj.get(SpeakerParamKey.PITCH) else speak_param_obj.get(SpeakerParamKey.PITCH)
            speak_param_obj[SpeakerParamKey.ALPHA] = speak_obj.get(SpeakerParamKey.ALPHA) if speak_obj.get(SpeakerParamKey.ALPHA) else speak_param_obj.get(SpeakerParamKey.ALPHA)
            speak_param_obj[SpeakerParamKey.INTONATION] = speak_obj.get(SpeakerParamKey.INTONATION) if speak_obj.get(SpeakerParamKey.INTONATION) else speak_param_obj.get(SpeakerParamKey.INTONATION)
            speak_param_obj[SpeakerParamKey.EMOTION_EP] = speak_obj.get(SpeakerParamKey.EMOTION_EP) if speak_obj.get(SpeakerParamKey.EMOTION_EP) else speak_param_obj.get(SpeakerParamKey.EMOTION_EP)
            speak_param_obj[SpeakerParamKey.EMOTION_P] = speak_obj.get(SpeakerParamKey.EMOTION_P) if speak_obj.get(SpeakerParamKey.EMOTION_P) else speak_param_obj.get(SpeakerParamKey.EMOTION_P)
            speak_param_obj[SpeakerParamKey.OVER_BANNER] = speak_obj.get(SpeakerParamKey.OVER_BANNER) if speak_obj.get(SpeakerParamKey.OVER_BANNER) else speak_param_obj.get(SpeakerParamKey.OVER_BANNER)
        else:
            speak_param_obj[SpeakerParamKey.ASYNC] = speak_obj.get(SpeakerParamKey.ASYNC)
            speak_param_obj[SpeakerParamKey.VOLUME] = speak_obj.get(SpeakerParamKey.VOLUME)
            speak_param_obj[SpeakerParamKey.SPEED] = speak_obj.get(SpeakerParamKey.SPEED)
            speak_param_obj[SpeakerParamKey.PITCH] = speak_obj.get(SpeakerParamKey.PITCH)
            speak_param_obj[SpeakerParamKey.ALPHA] = speak_obj.get(SpeakerParamKey.ALPHA)
            speak_param_obj[SpeakerParamKey.INTONATION] = speak_obj.get(SpeakerParamKey.INTONATION)
            speak_param_obj[SpeakerParamKey.EMOTION_EP] = speak_obj.get(SpeakerParamKey.EMOTION_EP)
            speak_param_obj[SpeakerParamKey.EMOTION_P] = speak_obj.get(SpeakerParamKey.EMOTION_P)
            speak_param_obj[SpeakerParamKey.OVER_BANNER] = speak_obj.get(SpeakerParamKey.OVER_BANNER)

        return cid, text, speak_param_obj

    def get_speaker_list(self):
        self.cids, self.speakers = self.seikasay2.list()
        return self.cids, self.speakers

    def get_speaker_name(self, cid):
        self.logger.debug(cid)
        for speaker in self.speakers:
            if speaker.startswith(cid):
                self.logger.debug(speaker)
                try:
                    return re.sub("^"+cid, "", speaker).split(" - ")[0].strip()
                except:
                    self.logger.debug("except")
                    return None
        return None

    def speak(self, cid, text, speak_param_obj={}):
        if cid and text:
            speaked_text = self.seikasay2.speak( \
                cid=cid, \
                text=text, \
                asynchronize=speak_param_obj.get(SpeakerParamKey.ASYNC), \
                volume=speak_param_obj.get(SpeakerParamKey.VOLUME), \
                speed=speak_param_obj.get(SpeakerParamKey.SPEED), \
                pitch=speak_param_obj.get(SpeakerParamKey.PITCH), \
                alpha=speak_param_obj.get(SpeakerParamKey.ALPHA), \
                intonation=speak_param_obj.get(SpeakerParamKey.INTONATION), \
                emotionEP=speak_param_obj.get(SpeakerParamKey.EMOTION_EP), \
                emotionP=speak_param_obj.get(SpeakerParamKey.EMOTION_P), \
                overBanner=speak_param_obj.get(SpeakerParamKey.OVER_BANNER) \
            )
            return speaked_text
        else:
            return None

    def on_message(self, ws, message):
        parsed = self.parse(json.loads(message))
        if parsed:
            self.logger.debug(parsed)
            cid = ""
            text = ""
            speak_param_obj = {}
            cid, text, speak_param_obj = self.gen_text(parsed)
            if cid and text:
                speaker = self.get_speaker_name(cid)
                if not speaker:
                    speaker = ""
                self.master_text.insert("end", speaker+"「"+text+"」\n")
                self.master_text.yview_moveto(1)
                speaked_text = self.speak(cid, text, speak_param_obj)
                if speaked_text:
                    self.logger.info(speaked_text)

    def on_error(self, ws, error):
        self.logger.error("error: called on_error")
        self.logger.error(error)

    def on_close(self, ws, close_status_code, close_msg):
        self.logger.info("### websocket is closed ###")
        if close_status_code:
            self.logger.info("close_status_code: {}".format(close_status_code))
        if close_msg:
            self.logger.info("close message: {}".format(close_msg))

    def on_open(self, ws):
        def run(*args):
            self.logger.info("### websocket is opened ###")

            while(True):
                line = sys.stdin.readline()
                if line != "":
                    self.logger.debug("debug: sending value is " + line)
                    ws.send(line)

        _thread.start_new_thread(run, ())

    def process_running_check(self, process_postfix):
        for proc in psutil.process_iter():
            try:
                if proc.exe().endswith(process_postfix):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    def speak_config(self):
        if self.config[ConfigKey.HERO_COMMENTARY_TYPE] == ConfigValue.SPEAKER1 and self.config[ConfigKey.OPPONENT_COMMENTARY_TYPE] == ConfigValue.SPEAKER1:
            self.speak(self.config[ConfigKey.SPEAKER1][ConfigKey.CID], "自分と対戦相手のアクションを実況します。")
        elif self.config[ConfigKey.HERO_COMMENTARY_TYPE] == ConfigValue.SPEAKER1 and self.config[ConfigKey.OPPONENT_COMMENTARY_TYPE] == ConfigValue.SPEAKER2:
            self.speak(self.config[ConfigKey.SPEAKER1][ConfigKey.CID], "自分のアクションを実況します。")
            self.speak(self.config[ConfigKey.SPEAKER2][ConfigKey.CID], "対戦相手のアクションを実況します。")
        elif self.config[ConfigKey.HERO_COMMENTARY_TYPE] == ConfigValue.SPEAKER1:
            self.speak(self.config[ConfigKey.SPEAKER1][ConfigKey.CID], "自分のアクションだけを実況します。")
        elif self.config[ConfigKey.OPPONENT_COMMENTARY_TYPE] == ConfigValue.SPEAKER1:
            self.speak(self.config[ConfigKey.SPEAKER1][ConfigKey.CID], "対戦相手のアクションだけを実況します。")
        elif self.config[ConfigKey.OPPONENT_COMMENTARY_TYPE] == ConfigValue.SPEAKER2:
            self.speak(self.config[ConfigKey.SPEAKER2][ConfigKey.CID], "対戦相手のアクションを実況します。")

    def run(self):
        self.logger.info("mtgatracker_backend.exe running check")
        running = False
        while not running:
            running = self.process_running_check(ProcessName.MTGATRACKER_BACKEND)
            if not running:
                ans = messagebox.askyesno(__file__, "{} プロセスが見つかりませんでした。\nmtgatracker_backendが起動していない可能性があります。\nはい: 再試行\nいいえ: 無視して続行".format(ProcessName.MTGATRACKER_BACKEND))
                if ans == True:
                    pass
                elif ans == False:
                    self.logger.info("mtgatracker_backend.exe running check: NG")
                    running = True
            else:
                self.logger.info("mtgatracker_backend.exe running check: OK")

        self.logger.info("AssistantSeika running check")
        running = False
        while not running:
            running = self.process_running_check(ProcessName.ASSISTANT_SEIKA)
            if not running:
                ans = messagebox.askyesno(__file__, "{} プロセスが見つかりませんでした。\nAssistantSeikaが起動していない可能性があります。\nはい: 再試行\nいいえ: 無視して続行".format(ProcessName.ASSISTANT_SEIKA))
                if ans == True:
                    pass
                elif ans == False:
                    self.logger.info("AssistantSeika running check: NG")
                    running = True
            else:
                self.logger.info("AssistantSeika running check: OK")

        self.logger.info("Get speakers from AssistantSeika")
        running = False
        while not running:
            self.get_speaker_list()
            if self.cids:
                running = True
                self.logger.info("Get cids from AssistantSeika: OK")
                break
            else:
                ans = messagebox.askyesno(__file__, "AssistantSeikaの話者一覧が空です。\n製品スキャンが未実行か、AssistantSeikaに対応している音声合成製品が未起動である可能性があります。\nはい: 再試行\nいいえ: 無視して続行")
                if ans == True:
                    pass
                elif ans == False:
                    self.logger.info("Get cids from AssistantSeika: NG")
                    running = True
        
        self.logger.debug(self.speakers)

        if not self.config.get(ConfigKey.SPEAKER1).get(ConfigKey.CID):
            self.config[ConfigKey.SPEAKER1][ConfigKey.CID] = self.cids[0]
        if not self.config.get(ConfigKey.SPEAKER2).get(ConfigKey.CID):
            self.config[ConfigKey.SPEAKER2][ConfigKey.CID] = self.cids[0]
        
        if not self.config[ConfigKey.SPEAKER1][ConfigKey.CID] in self.cids:
            self.config[ConfigKey.SPEAKER1][ConfigKey.CID] = self.cids[0]
        if not self.config[ConfigKey.SPEAKER2][ConfigKey.CID] in self.cids:
            self.config[ConfigKey.SPEAKER2][ConfigKey.CID] = self.cids[0]
            if self.config[ConfigKey.OPPONENT_COMMENTARY_TYPE] == ConfigValue.SPEAKER2:
                self.config[ConfigKey.OPPONENT_COMMENTARY_TYPE] = ConfigValue.SPEAKER1

        self.open_config_window()
        self.logger.info("話者1: {}".format(self.config.get(ConfigKey.SPEAKER1).get(ConfigKey.NAME)))
        self.logger.info("話者2: {}".format(self.config.get(ConfigKey.SPEAKER2).get(ConfigKey.NAME)))
        self.load_speakers()

        self.start_ws_client()
        self.speak_config()

        self.master.mainloop()
        #try:
        #    self.ws.run_forever()
        #except KeyboardInterrupt:
        #    self.ws.close()

        self.ws.close()

if __name__ == "__main__":
    #param = sys.argv
    root = tkinter.Tk()
    commentary_backend = CommentaryBackend(master=root)
    commentary_backend.run()
