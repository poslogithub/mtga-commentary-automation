import _thread
from datetime import datetime
from enum import Enum
import json
import logging
import logging.handlers
import os
import re
import sys
from threading import Thread
from time import sleep
import asyncio
import aiohttp
import tkinter
from tkinter import StringVar, filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from urllib.parse import quote
from urllib.request import urlopen
from http.client import RemoteDisconnected
import requests
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
    CREATES = "creates"
    DRAWS = "draws"
    EXILES = "exiles"
    LIFE_TOTAL_CHANGED = "'s life total changed"
    PLAYS = "plays"
    RESOLVES = "resolves"
    SENT_TO_GRAVEYARD = "sent to graveyard"
    STARTING_HAND = "'s starting hand:"
    VS = "vs"

class Reason:
    # message from mtgatracker_backend
    CONJURE = "(Conjure)"
    DESTROY = "(Destroy)"
    DISCARD = "(Discard)"
    MILL = "(Mill)"
    PUT = "(Put)"
    SACRIFICE = "(Sacrifice)"
    SBA_DAMEGE = "(SBA_Damage)"
    SBA_DEATHTOUCH = "(SBA_Deathtouch)",
    SBA_ZERO_LOYALTY = "(SBA_ZeroLoyalty)"
    SBA_ZERO_TOUGHNESS = "(SBA_ZeroToughness)"
    SBA_UNATTACHED_AURA = "(SBA_UnattachedAura)"
    NIL = "(nil)"


class ParseKey:
    IS_OPPONENT = "isOpponent"
    MESSAGE_TYPE = "messageType"
    EVENT = "event"
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
    WAV_OUTPUT = "wavOutput"
    YUKARINETTE_CONNECTOR_NEO = "yukarinetteConnectorNeo"
    YUKARINETTE_CONNECTOR_NEO_URL = "yukarinetteConnectorNeoUrl"

class ConfigValue:
    SPEAKER1 = "speaker1"
    SPEAKER2 = "speaker2"
    NEVER = "never"


class SpeakerKey:
    SPEAK = "speak"
    TEXT = MessageKey.TEXT
    EVENT = ParseKey.EVENT
    TYPE = MessageKey.TYPE

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
    GAME_START = "??????????????????"
    GAME_WIN = "??????????????????"
    GAME_LOSE = "??????????????????"
    MULLIGAN_CHECK = "???????????????????????????"
    TURN_START = "??????????????????"
    DRAW = "????????????????????????"
    DISCARD = "????????????????????????"
    PLAY_LAND = "???????????????????????????"
    CAST_SPELL = "?????????????????????"
    COUNTERED = "??????????????????????????????"
    CREATE_TOKEN = "?????????????????????????????????"
    RESOLVE = "????????????????????????"
    EXILE = "??????????????????????????????"
    CONJURE = "????????????????????????????????????????????????"
    DESTROY = "????????????????????????????????????????????????"
    MILL = "????????????????????????????????????????????????"
    PUT = "????????????????????????????????????????????????"
    SACRIFICE = "???????????????????????????????????????????????????"
    DIE = "????????????????????????????????????????????????"
    UNATTACHED_AURA = "?????????????????????????????????????????????????????????"
    NIL = "?????????????????????????????????????????????????????????"
    ATTACK = "?????????????????????????????????"
    BLOCK = "???????????????????????????????????????"
    LIFE_GAIN = "????????????????????????"
    LIFE_LOSE = "????????????????????????"

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
    CREATE_TOKEN = "CreateToken"
    RESOLVE = "Resolve"
    ATTACK = "Attack"
    BLOCK = "Block"
    LIFE_GAIN = "LifeGain"
    LIFE_LOSE = "LifeLose"
    DIE = "Die"
    DESTROY = "Destroy"
    SACRIFICE = "Sacrifice"
    EXILE = "Exile"
    PUT_INTO_GRAVEYARD = "PutIntoGraveyard"
    CONJURE = "Conjure"

class SpeakerWindowEntry(Enum):
    # (?????????, ?????????text, textvariable)
    GAME_START = (Event.GAME_START, "??????????????????:")
    GAME_WIN = (Event.GAME_WIN, "??????????????????:")
    GAME_LOSE = (Event.GAME_LOSE, "??????????????????:")
    MULLIGAN_CHECK = (Event.MULLIGAN_CHECK, "???????????????????????????:")
    TURN_START = (Event.TURN_START, "??????????????????:")
    DRAW = (Event.DRAW, "????????????????????????:")
    DISCARD = (Event.DISCARD, "????????????????????????:")
    PLAY_LAND = (Event.PLAY_LAND, "???????????????????????????:")
    CAST_SPELL = (Event.CAST_SPELL, "?????????????????????:")
    COUNTERED = (Event.COUNTERED, "??????????????????????????????:")
    CREATE_TOKEN = (Event.CREATE_TOKEN, "?????????????????????????????????:")
    RESOLVE = (Event.RESOLVE, "???????????????????????????:")
    ATTACK = (Event.ATTACK, "?????????????????????????????????:")
    BLOCK = (Event.BLOCK, "???????????????????????????????????????:")
    LIFE_GAIN = (Event.LIFE_GAIN, "????????????????????????:")
    LIFE_LOSE = (Event.LIFE_LOSE, "????????????????????????:")
    DIE = (Event.DIE, "????????????????????????????????????:")
    DESTROY = (Event.DESTROY, "???????????????????????????????????????:")
    SACRIFICE = (Event.SACRIFICE, "?????????????????????????????????????????????:")
    EXILE = (Event.EXILE, "??????????????????????????????:")
    PUT_INTO_GRAVEYARD = (Event.PUT_INTO_GRAVEYARD, "????????????????????????????????????:")
    CONJURE = (Event.CONJURE, "??????????????????????????????:")


class ProcessName:
    ASSISTANT_SEIKA = "AssistantSeika.exe"
    MTGATRACKER_BACKEND = "mtgatracker_backend.exe"
    SEIKA_SAY2 = "SeikaSay2.exe"


class CommentaryBackend(tkinter.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        # ??????
        self.CONFIG_FILE = "config\\config.json"
        self.DEFAULT_SPEAKER_FILE = "config\\defaultSpeaker.json"
        self.LOG_FILE = os.path.basename(__file__).split(".")[0]+".log"
        self.BAT_FOR_WAV_FILE = "WAV??????????????????_{}.bat".format(datetime.now().strftime('%Y%m%d_%H%M%S'))
        self.WAV_OUTPUT_DIR = os.getcwd()+"\\wav"

        # ??????
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
            ConfigKey.MTGATRACKER_BACKEND_URL : "ws://localhost:8089",
            ConfigKey.WAV_OUTPUT : False,
            ConfigKey.YUKARINETTE_CONNECTOR_NEO : False,
            ConfigKey.YUKARINETTE_CONNECTOR_NEO_URL : "http://localhost:15520/api/input?text="
        }
        self.no_assistant_seika = False
        self.cids = []
        self.speakers = []
        self.speaker1_obj = {}
        self.speaker2_obj = {}
        self.hero_screen_name = ""
        self.opponent_screen_name = ""
        self.HERO_COMMENTARY_TYPES = ["??????1???????????????????????????", "???????????????"]
        self.OPPONENT_COMMENTARY_TYPES = ["??????1???????????????????????????", "??????2???????????????????????????", "???????????????"]
        self.WAV_OUTPUT = ["WAV??????????????????????????????", "WAV?????????????????????bat???????????????????????????"]
        self.YUKARINETTE_CONNECTOR_NEO = ["???????????????", "????????????????????????????????? Neo??????????????????????????????"]

        # GUI
        self.master.title("MTGA?????????????????????")
        self.master.geometry("600x360")
        self.master_frame = tkinter.Frame(self.master)
        self.master_frame.pack()
        self.master_text = ScrolledText(self.master_frame, state='disabled')
        self.master_text.pack()
        self.master_quit = tkinter.Button(self.master_frame, text="????????????", command=self.master_frame_quit)
        self.master_quit.pack(fill='x', padx=10, pady=5, side = 'right')
        self.master_save = tkinter.Button(self.master_frame, text="????????????", command=self.master_frame_save)
        self.master_save.pack(fill='x', padx=10, pady=5, side = 'right')

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
                print("??????: {} ?????????????????????????????????????????????????????????????????????????????????????????????".format(self.LOG_FILE))
        self.logger.addHandler(stream_handler)
        self.logger.addHandler(rotating_handler)

        # load config
        self.logger.info("Loading {}".format(self.CONFIG_FILE))
        if self.load_config():
            self.logger.info("Loading {}: OK".format(self.CONFIG_FILE))
        else:
            self.logger.info("Loading {}: NG".format(self.CONFIG_FILE))

    def master_frame_save(self):
        filename = "MTGA????????????_{}.txt".format(datetime.now().strftime('%Y%m%d_%H%M%S'))
        path = filedialog.asksaveasfilename(filetype=[("????????????????????????","*.txt")], initialdir=os.getcwd(), initialfile=filename)
        if path:
            with open(path, 'a', encoding="utf_8_sig") as af:
                af.write(self.master_text.get("1.0","end"))

    def master_frame_quit(self):
        if messagebox.askyesno("????????????", "????????????????????????????????????"):
            self.master.destroy()

    def start_ws_client(self):
        t = Thread(target=self.connect_to_socket)
        t.daemon = True
        t.start()

    def connect_to_socket(self):
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp(self.config.get(ConfigKey.MTGATRACKER_BACKEND_URL),
            on_open = self.on_open,
            on_message = self.on_message,
            on_error = self.on_error,
            on_close = self.on_close)
        self.ws.run_forever()

    def send_text_to_yukarinette_conecctor_neo(self, text):
        try:
            urlopen(url=self.config.get(ConfigKey.YUKARINETTE_CONNECTOR_NEO_URL) + quote(text), timeout=5)
        except:
            pass

    def load_config(self, config_file=None):
        if not config_file:
            config_file = self.CONFIG_FILE
        if not os.path.exists(config_file):
            self.save_config(config_file, self.config)
        with open(config_file if config_file else self.CONFIG_FILE, 'r', encoding="utf_8_sig") as rf:
            self.config = json.load(rf)
            if self.config.get(ConfigKey.WAV_OUTPUT) is None:
                self.config[ConfigKey.WAV_OUTPUT] = False
            if self.config.get(ConfigKey.YUKARINETTE_CONNECTOR_NEO) is None:
                self.config[ConfigKey.YUKARINETTE_CONNECTOR_NEO] = False
            if self.config.get(ConfigKey.YUKARINETTE_CONNECTOR_NEO_URL) is None:
                self.config[ConfigKey.YUKARINETTE_CONNECTOR_NEO_URL] = "http://localhost:15520/api/input?text="
        return self.config
    
    def save_config(self, config_file=None, config=None):
        with open(config_file if config_file else self.CONFIG_FILE, 'w', encoding="utf_8_sig") as wf:
            json.dump(config if config else self.config, wf, indent=4, ensure_ascii=False)
    
    def open_config_window(self):
        speaker1_index = self.cids.index(self.config.get(ConfigKey.SPEAKER1).get(ConfigKey.CID))
        speaker2_index = self.cids.index(self.config.get(ConfigKey.SPEAKER2).get(ConfigKey.CID))
        self.config_window = tkinter.Toplevel(self)
        self.config_window.title("MTGA????????????????????? - ?????????????????????")
        self.config_window.geometry("520x250")
        self.config_window.grab_set()   # ?????????????????????
        self.config_window.focus_set()  # ??????????????????????????????????????????????????????
        self.config_window.transient(self.master)   # ?????????????????????????????????
        self.config_frame = ttk.Frame(self.config_window)
        self.config_frame.grid(column=0, row=0, sticky=tkinter.NSEW, padx=5, pady=5)
        self.sv_seikasay2_path = tkinter.StringVar()
        self.sv_seikasay2_path.set(self.config.get(ConfigKey.SEIKA_SAY2_PATH))
        self.sv_speaker1 = tkinter.StringVar()
        self.sv_speaker2 = tkinter.StringVar()
        self.sv_hero_commentary_type = tkinter.StringVar()
        self.sv_opponent_commentary_type = tkinter.StringVar()
        self.sv_wav_output = tkinter.StringVar()
        self.sv_yukarinette_connector_neo = tkinter.StringVar()
        combobox_width = 44
        button_seikasay2 = tkinter.Button(self.config_frame, text="????????????", command=self.config_window_seikasay2)
        button_seikasay2.grid(row=0, column=2, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        label_speaker1 = ttk.Label(self.config_frame, text="??????1: ", anchor="w")
        label_speaker1.grid(row=0, column=0, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        combobox_speaker1 = ttk.Combobox(self.config_frame, width=combobox_width, values=self.speakers, textvariable=self.sv_speaker1, state="readonly")
        combobox_speaker1.current(speaker1_index)
        combobox_speaker1.grid(row=0, column=1, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        button_speaker1 = tkinter.Button(self.config_frame, text="????????????", command=lambda: self.open_speaker_window(self.sv_speaker1.get().split(" ")[0]))
        button_speaker1.grid(row=0, column=2, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        label_speaker2 = ttk.Label(self.config_frame, text="??????2: ", anchor="w")
        label_speaker2.grid(row=1, column=0, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        combobox_speaker2 = ttk.Combobox(self.config_frame, width=combobox_width, values=self.speakers, textvariable=self.sv_speaker2, state="readonly")
        combobox_speaker2.current(speaker2_index)
        combobox_speaker2.grid(row=1, column=1, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        button_speaker2 = tkinter.Button(self.config_frame, text="????????????", command=lambda: self.open_speaker_window(self.sv_speaker2.get().split(" ")[0]))
        button_speaker2.grid(row=1, column=2, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        label_hero_commentary_type = ttk.Label(self.config_frame, text="????????????????????????: ", anchor="w")
        label_hero_commentary_type.grid(row=2, column=0, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        combobox_hero_commentary_type = ttk.Combobox(self.config_frame, width=combobox_width, values=self.HERO_COMMENTARY_TYPES, textvariable=self.sv_hero_commentary_type, state="readonly")
        combobox_hero_commentary_type.current(0 if self.config.get(ConfigKey.HERO_COMMENTARY_TYPE) == ConfigValue.SPEAKER1 else 1)
        combobox_hero_commentary_type.grid(row=2, column=1, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        label_opponent_commentary_type = ttk.Label(self.config_frame, text="??????????????????????????????: ", anchor="w")
        label_opponent_commentary_type.grid(row=3, column=0, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        combobox_opponent_commentary_type = ttk.Combobox(self.config_frame, width=combobox_width, values=self.OPPONENT_COMMENTARY_TYPES, textvariable=self.sv_opponent_commentary_type, state="readonly")
        combobox_opponent_commentary_type.current(0 if self.config.get(ConfigKey.OPPONENT_COMMENTARY_TYPE) == ConfigValue.SPEAKER1 else 1 if self.config.get(ConfigKey.OPPONENT_COMMENTARY_TYPE) == ConfigValue.SPEAKER2 else 2)
        combobox_opponent_commentary_type.grid(row=3, column=1, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        label_wav_output = ttk.Label(self.config_frame, text="WAV??????????????????: ", anchor="w")
        label_wav_output.grid(row=4, column=0, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        combobox_wav_output = ttk.Combobox(self.config_frame, width=combobox_width, values=self.WAV_OUTPUT, textvariable=self.sv_wav_output, state="readonly")
        combobox_wav_output.current(0 if not self.config.get(ConfigKey.WAV_OUTPUT) else 1)
        combobox_wav_output.grid(row=4, column=1, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        label_yukarinette_connector_neo = ttk.Label(self.config_frame, text="????????????????????????????????? Neo: ", anchor="w")
        label_yukarinette_connector_neo.grid(row=5, column=0, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        combobox_yukarinette_connector_neo = ttk.Combobox(self.config_frame, width=combobox_width, values=self.YUKARINETTE_CONNECTOR_NEO, textvariable=self.sv_yukarinette_connector_neo, state="readonly")
        combobox_yukarinette_connector_neo.current(0 if not self.config.get(ConfigKey.YUKARINETTE_CONNECTOR_NEO) else 1)
        combobox_yukarinette_connector_neo.grid(row=5, column=1, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        button_ok = tkinter.Button(self.config_frame, text="????????????", command=self.config_window_ok)
        button_ok.grid(row=6, column=2, sticky=tkinter.E, padx=5, pady=10)
        self.wait_window(self.config_window)
    
    def config_window_seikasay2(self):
        path = filedialog.askopenfilename(filetype=[("??????????????????","*.exe")], initialdir=os.getcwd())
        if path:
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
        self.config[ConfigKey.WAV_OUTPUT] = False if self.sv_wav_output.get() == self.WAV_OUTPUT[0] else True
        self.config[ConfigKey.YUKARINETTE_CONNECTOR_NEO] = False if self.sv_yukarinette_connector_neo.get() == self.YUKARINETTE_CONNECTOR_NEO[0] else True
        self.save_config()
        self.config_window.destroy()

    def config_window_cancel(self):
        self.config_window.destroy()

    def open_speaker1_window(self):
        self.open_speaker_window(self.sv_speaker1.get().split(" ")[0])

    def open_speaker2_window(self):
        self.open_speaker_window(self.sv_speaker2.get().split(" ")[0])

    def get_speak_obj(self, speakers, event):
        for obj in speakers:
            if obj.get(SpeakerKey.EVENT) == event:
                return obj.get(SpeakerKey.SPEAK)
        return None

    def open_speaker_window(self, cid):
        speakers = self.load_speaker(cid)
        self.speaker_window = tkinter.Toplevel(self.config_window)
        self.speaker_window.title("MTGA????????????????????? - ????????????????????? - {}".format(self.get_speaker_name(cid)))
        self.speaker_window.geometry("940x620")
        self.speaker_window.grab_set()   # ?????????????????????
        self.speaker_window.focus_set()  # ??????????????????????????????????????????????????????
        self.speaker_window.transient(self.master)   # ?????????????????????????????????
        self.speaker_frame = ttk.Frame(self.speaker_window)
        self.speaker_frame.grid(column=0, row=0, sticky=tkinter.NSEW, padx=5, pady=5)
        
        label1 = ttk.Label(self.speaker_frame, text="???????????????????????????????????????", anchor="w")
        label1.grid(row=0, column=1, sticky=tkinter.W + tkinter.E, padx=4, pady=2)
        label2 = ttk.Label(self.speaker_frame, text="?????????????????????????????????????????????", anchor="w")
        label2.grid(row=0, column=2, sticky=tkinter.W + tkinter.E, padx=4, pady=2)
        label3 = ttk.Label(self.speaker_frame, text="?????????????????????????????????????????????", anchor="w")
        label3.grid(row=0, column=3, sticky=tkinter.W + tkinter.E, padx=4, pady=2)

        labels = {}
        svs = {}
        entrys = {}
        i = 1
        for key in SpeakerWindowEntry:
            labels[key.name] = ttk.Label(self.speaker_frame, text=key.value[1], anchor="w")
            labels[key.name].grid(row=i, column=0, sticky=tkinter.W + tkinter.E, padx=4, pady=2)
            svs[key.name] = []
            entrys[key.name] = []
            for j in range(3):
                svs[key.name].append(StringVar())
                svs[key.name][j].set(self.get_speak_obj(speakers, key.value[0])[j].get(SpeakerKey.TEXT))
                entrys[key.name].append(ttk.Entry(self.speaker_frame, width=40, textvariable=svs[key.name][j]))
                entrys[key.name][j].grid(row=i, column=j+1, sticky=tkinter.W + tkinter.E, padx=4, pady=2)
                if j > 0 and key.value[0] in [Event.GAME_START, Event.GAME_WIN, Event.GAME_LOSE, Event.MULLIGAN_CHECK]:
                    entrys[key.name][j].config(state='disabled')
            i += 1
        
        button_ok = tkinter.Button(self.speaker_frame, text="?????????????????????", command=lambda: self.speaker_window_ok(cid, speakers, svs))
        button_ok.grid(row=i, column=2, sticky=tkinter.W + tkinter.E, padx=4, pady=10)
        button_cancel = tkinter.Button(self.speaker_frame, text="???????????????????????????", command=self.speaker_window_cancel)
        button_cancel.grid(row=i, column=3, sticky=tkinter.W + tkinter.E, padx=4, pady=10)
        self.wait_window(self.speaker_window)

    def speaker_window_ok(self, cid, speakers, svs):
        for key in SpeakerWindowEntry:
            for j in range(3):
                self.get_speak_obj(speakers, key.value[0])[j][SpeakerKey.TEXT] = svs[key.name][j].get()
        self.save_speaker(cid, speakers)
        self.speaker_window.destroy()

    def speaker_window_cancel(self):
        self.speaker_window.destroy()

    def load_speaker(self, cid):
        speaker_file = "config\\{}.json".format(cid)
        if not os.path.isfile(speaker_file):
            speaker_file = self.DEFAULT_SPEAKER_FILE
        with open(speaker_file, 'r', encoding="utf_8_sig") as rf:
            return json.load(rf)

    def save_speaker(self, cid, speaker):
        speaker_file = "config\\{}.json".format(cid)
        with open(speaker_file, 'w', encoding="utf_8_sig") as wf:
            json.dump(speaker, wf, ensure_ascii=False)
    
    def del_ruby(self, s):
        return re.sub("???.+????", "", re.sub("<.+?>", "", s))

    def parse(self, blob):
        self.logger.debug(blob)
        if blob:
            text_array = blob.get(MessageKey.GAME_HISTORY_EVENT)
            if not text_array:
                return None
            parsed = {}

            if len(text_array) == 0:
                self.logger.warning("warning: ??????0???text_array")
            elif len(text_array) == 1:
                if text_array[0].get(MessageKey.TYPE) == MessageValue.GAME: # ???????????????  {"text": "screenName won!", "type": "game"}
                    parsed[ParseKey.MESSAGE_TYPE] = text_array[0].get(MessageKey.TYPE)
                    if text_array[0].get(MessageKey.TEXT).startswith(self.hero_screen_name):
                        parsed[ParseKey.EVENT] = Event.GAME_WIN
                    else:
                        parsed[ParseKey.EVENT] = Event.GAME_LOSE
                elif text_array[0].get(MessageKey.TYPE) == MessageValue.TURN:   # ???????????????  { "text": "N / screenName Turn M", "type": "turn" }
                    if text_array[0].get(MessageKey.TEXT).find(self.opponent_screen_name) >= 0:
                        parsed[ParseKey.IS_OPPONENT] = True
                    parsed[ParseKey.MESSAGE_TYPE] = text_array[0].get(MessageKey.TYPE)
                    parsed[ParseKey.EVENT] = Event.TURN_START
                else:
                    self.logger.warning("warning: ?????????type: {}".format(text_array[0].get(MessageKey.TYPE)))
            else:
                parsed[ParseKey.VERB] = text_array[1].strip()

                # ?????????"'s"????????????????????????????????????
                if parsed.get(ParseKey.VERB) == "'s":   # { "text": ????????????, "type": hero/opponent }, "'s ", { "text": ability, "type": "ability"}, ...
                    parsed[ParseKey.SOURCE] = text_array[0].get(MessageKey.TEXT)
                    parsed[ParseKey.IS_OPPONENT] = True if text_array[0].get(MessageKey.TYPE) == MessageValue.OPPONENT else False
                    parsed[ParseKey.MESSAGE_TYPE] = text_array[2].get(MessageKey.TYPE)    # ability

                    # ":"????????????????????????"'s"???????????????????????????
                    if len(text_array) >= 4 and text_array[3].strip() != ":":   # ex: "CARDNAME1 's ability exiles CARDNAME2"
                        text_array = text_array[2:]

                    # ":"??????????????????":"???????????????????????????
                    elif len(text_array) >= 6 and text_array[3].strip() == ":": # ex: "CARDNAME1 's ability : SCREENNAME draws CARDNAME2"
                        text_array = text_array[4:]
                    parsed[ParseKey.VERB] = text_array[1].strip()

                # ?????????":"????????????":"???????????????????????????
                if parsed.get(ParseKey.VERB) == ":":    # { "text": ????????????, "type": "opponent" }, ": ", { "text": screenName, "type": "opponent" }, ...
                    parsed[ParseKey.SOURCE] = text_array[0].get(MessageKey.TEXT)
                    if len(text_array) >= 4:   # ex: "CARDNAME1 : SCREENNAME draws CARDNAME2"
                        text_array = text_array[2:]
                    parsed[ParseKey.VERB] = text_array[1].strip()

                if parsed.get(ParseKey.VERB) == Verb.ATTAKING:  # ?????????????????????????????????  { "text": ????????????, "type": hero/opponent }, " attacking"
                    parsed[ParseKey.IS_OPPONENT] = True if text_array[0].get(MessageKey.TYPE) == MessageValue.OPPONENT else False
                    parsed[ParseKey.ATTACKER] = self.del_ruby(text_array[0].get(MessageKey.TEXT))
                    parsed[ParseKey.CARD] = parsed[ParseKey.ATTACKER]   # ????????????
                    parsed[ParseKey.EVENT] = Event.ATTACK
                elif parsed.get(ParseKey.VERB) == Verb.BLOCKS:
                    parsed[ParseKey.IS_OPPONENT] = True if text_array[0].get(MessageKey.TYPE) == MessageValue.OPPONENT else False
                    parsed[ParseKey.BLOCKER] = self.del_ruby(text_array[0].get(MessageKey.TEXT))
                    parsed[ParseKey.ATTACKER] = self.del_ruby(text_array[2].get(MessageKey.TEXT))
                    parsed[ParseKey.CARD] = parsed[ParseKey.BLOCKER]   # ????????????
                    parsed[ParseKey.SOURCE] = parsed[ParseKey.BLOCKER]   # ????????????
                    parsed[ParseKey.TARGET] = parsed[ParseKey.ATTACKER]   # ????????????
                    parsed[ParseKey.EVENT] = Event.BLOCK
                elif parsed.get(ParseKey.VERB) == Verb.CASTS:
                    parsed[ParseKey.IS_OPPONENT] = True if text_array[0].get(MessageKey.TYPE) == MessageValue.OPPONENT else False
                    parsed[ParseKey.CARD] = self.del_ruby(text_array[2].get(MessageKey.TEXT))
                    parsed[ParseKey.EVENT] = Event.CAST_SPELL
                elif parsed.get(ParseKey.VERB) == Verb.COUNTERS:
                    parsed[ParseKey.IS_OPPONENT] = True if text_array[0].get(MessageKey.TYPE) == MessageValue.OPPONENT else False
                    parsed[ParseKey.SOURCE] = self.del_ruby(text_array[0].get(MessageKey.TEXT))
                    parsed[ParseKey.TARGET] = self.del_ruby(text_array[2].get(MessageKey.TEXT))
                    parsed[ParseKey.CARD] = parsed[ParseKey.TARGET] # ????????????
                    parsed[ParseKey.EVENT] = Event.COUNTERED
                elif parsed.get(ParseKey.VERB) == Verb.CREATES:
                    parsed[ParseKey.IS_OPPONENT] = True if text_array[2].get(MessageKey.TYPE) == MessageValue.OPPONENT else False
                    parsed[ParseKey.SOURCE] = self.del_ruby(text_array[0].get(MessageKey.TEXT))
                    parsed[ParseKey.TARGET] = self.del_ruby(text_array[2].get(MessageKey.TEXT))
                    parsed[ParseKey.CARD] = self.del_ruby(text_array[2].get(MessageKey.TEXT))
                    parsed[ParseKey.EVENT] = Event.CREATE_TOKEN
                elif parsed.get(ParseKey.VERB) == Verb.DRAWS:
                    parsed[ParseKey.IS_OPPONENT] = True if text_array[0].get(MessageKey.TYPE) == MessageValue.OPPONENT else False
                    if len(text_array) >= 3:
                        parsed[ParseKey.CARD] = self.del_ruby(text_array[2].get(MessageKey.TEXT))
                        parsed[ParseKey.TARGET] = parsed[ParseKey.CARD] # ????????????
                    parsed[ParseKey.EVENT] = Event.DRAW
                elif parsed.get(ParseKey.VERB) == Verb.EXILES:
                    parsed[ParseKey.IS_OPPONENT] = True if text_array[2].get(MessageKey.TYPE) == MessageValue.OPPONENT else False
                    parsed[ParseKey.CARD] = self.del_ruby(text_array[2].get(MessageKey.TEXT))
                    parsed[ParseKey.TARGET] = parsed[ParseKey.CARD] # ????????????
                    parsed[ParseKey.EVENT] = Event.EXILE
                elif parsed.get(ParseKey.VERB) == Verb.LIFE_TOTAL_CHANGED:
                    parsed[ParseKey.IS_OPPONENT] = True if text_array[0].get(MessageKey.TYPE) == MessageValue.OPPONENT else False
                    parsed[ParseKey.LIFE_FROM] = int(text_array[2].split(" -> ")[0])
                    parsed[ParseKey.LIFE_TO] = int(text_array[2].split(" -> ")[1])
                    parsed[ParseKey.SOURCE] = parsed[ParseKey.LIFE_FROM] # ????????????
                    parsed[ParseKey.TARGET] = parsed[ParseKey.LIFE_TO] # ????????????
                    parsed[ParseKey.EVENT] = Event.LIFE_GAIN if parsed[ParseKey.LIFE_FROM] < parsed[ParseKey.LIFE_TO] else Event.LIFE_LOSE
                    parsed[ParseKey.LIFE_DIFF] = abs(parsed[ParseKey.LIFE_TO] - parsed[ParseKey.LIFE_FROM])
                elif parsed.get(ParseKey.VERB) == Verb.PLAYS:
                    parsed[ParseKey.IS_OPPONENT] = True if text_array[0].get(MessageKey.TYPE) == MessageValue.OPPONENT else False
                    parsed[ParseKey.CARD] = self.del_ruby(text_array[2].get(MessageKey.TEXT))
                    parsed[ParseKey.TARGET] = parsed[ParseKey.CARD] # ????????????
                    parsed[ParseKey.EVENT] = Event.PLAY_LAND
                elif parsed.get(ParseKey.VERB) == Verb.RESOLVES:
                    parsed[ParseKey.IS_OPPONENT] = True if text_array[0].get(MessageKey.TYPE) == MessageValue.OPPONENT else False
                    parsed[ParseKey.CARD] = self.del_ruby(text_array[0].get(MessageKey.TEXT))
                    parsed[ParseKey.TARGET] = parsed[ParseKey.CARD] # ????????????
                    parsed[ParseKey.EVENT] = Event.RESOLVE
                elif parsed.get(ParseKey.VERB) == Verb.SENT_TO_GRAVEYARD:
                    parsed[ParseKey.IS_OPPONENT] = True if text_array[0].get(MessageKey.TYPE) == MessageValue.OPPONENT else False
                    parsed[ParseKey.CARD] = self.del_ruby(text_array[0].get(MessageKey.TEXT))
                    parsed[ParseKey.TARGET] = parsed[ParseKey.CARD] # ????????????
                    parsed[ParseKey.REASON] = text_array[2]
                    if parsed.get(ParseKey.REASON) in [Reason.SBA_DAMEGE, Reason.SBA_DEATHTOUCH, Reason.SBA_ZERO_TOUGHNESS, Reason.SBA_ZERO_LOYALTY]: # ???????????????????????????????????????????????????????????????0??????????????????0???
                        parsed[ParseKey.EVENT] = Event.DIE
                    elif parsed.get(ParseKey.REASON) in [Reason.DESTROY]: # ??????
                        parsed[ParseKey.EVENT] = Event.DESTROY
                    elif parsed.get(ParseKey.REASON) in [Reason.SACRIFICE]: # ?????????
                        parsed[ParseKey.EVENT] = Event.SACRIFICE
                    elif parsed.get(ParseKey.REASON) in [Reason.CONJURE]: # ??????
                        parsed[ParseKey.EVENT] = Event.CONJURE
                    elif parsed.get(ParseKey.REASON) in [Reason.DISCARD]: # ??????????????????
                        parsed[ParseKey.EVENT] = Event.DISCARD
                    elif parsed.get(ParseKey.REASON) in [Reason.MILL, Reason.PUT, Reason.SBA_UNATTACHED_AURA, Reason.NIL]: # ?????????????????????????????????????????????????????????????????????????????????????????????????????????
                        parsed[ParseKey.EVENT] = Event.PUT_INTO_GRAVEYARD
                    else:
                        self.logger.warning("warning: ?????????reason: {}".format(parsed.get(ParseKey.REASON)))
                elif parsed.get(ParseKey.VERB) == Verb.STARTING_HAND:
                    parsed[ParseKey.EVENT] = Event.MULLIGAN_CHECK
                elif parsed.get(ParseKey.VERB) == Verb.VS:
                    self.hero_screen_name = text_array[0].get(MessageKey.TEXT)
                    self.opponent_screen_name = text_array[2].get(MessageKey.TEXT)
                    parsed[ParseKey.SOURCE] = self.hero_screen_name # ???????????????
                    parsed[ParseKey.TARGET] = self.opponent_screen_name # ???????????????
                    parsed[ParseKey.EVENT] = Event.GAME_START
                else:
                    self.logger.warning("warning: ?????????verb: {}".format(parsed.get(ParseKey.VERB)))

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
        for obj in speaker:
            if obj.get(SpeakerKey.EVENT) == parsed.get(ParseKey.EVENT):
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
        for speaker in self.speakers:
            if speaker.startswith(cid):
                try:
                    return re.sub("^"+cid, "", speaker).split(" - ")[0].strip()
                except:
                    return None
        return None

    def speak(self, cid, text, speak_param_obj={}, save=True):
        if cid and text:
            if self.config.get(ConfigKey.YUKARINETTE_CONNECTOR_NEO) and save:
                # ????????????????????????????????? Neo????????????????????????
                t = Thread(target=self.send_text_to_yukarinette_conecctor_neo, args=(text,))
                t.daemon = True
                t.start()

            if not self.no_assistant_seika:
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
                if self.config.get(ConfigKey.WAV_OUTPUT) and save:
                    cmd = self.seikasay2.get_speak_command( \
                        cid=cid, \
                        text=text, \
                        asynchronize=speak_param_obj.get(SpeakerParamKey.ASYNC), \
                        save=self.WAV_OUTPUT_DIR+"\\"+datetime.now().strftime('%Y%m%d_%H%M%S_%f')+"_"+self.get_speaker_name(cid)+"???"+text+"???.wav", \
                        volume=speak_param_obj.get(SpeakerParamKey.VOLUME), \
                        speed=speak_param_obj.get(SpeakerParamKey.SPEED), \
                        pitch=speak_param_obj.get(SpeakerParamKey.PITCH), \
                        alpha=speak_param_obj.get(SpeakerParamKey.ALPHA), \
                        intonation=speak_param_obj.get(SpeakerParamKey.INTONATION), \
                        emotionEP=speak_param_obj.get(SpeakerParamKey.EMOTION_EP), \
                        emotionP=speak_param_obj.get(SpeakerParamKey.EMOTION_P), \
                        overBanner=speak_param_obj.get(SpeakerParamKey.OVER_BANNER) \
                    )
                    with open(self.BAT_FOR_WAV_FILE, 'a') as af:
                        af.write(cmd+"\n")
            else:
                speaked_text = text

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
                self.logger.info(speaker+"???"+text+"???")
                self.master_text.config(state="normal")
                self.master_text.insert("end", speaker+"???"+text+"???\n")
                self.master_text.yview_moveto(1)
                self.master_text.config(state="disabled")
                self.speak(cid, text, speak_param_obj)

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
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return None

    def speak_config(self):
        if self.config[ConfigKey.HERO_COMMENTARY_TYPE] == ConfigValue.SPEAKER1 and self.config[ConfigKey.OPPONENT_COMMENTARY_TYPE] == ConfigValue.SPEAKER1:
            self.speak(self.config[ConfigKey.SPEAKER1][ConfigKey.CID], "????????????????????????????????????????????????????????????", save=False)
        elif self.config[ConfigKey.HERO_COMMENTARY_TYPE] == ConfigValue.SPEAKER1 and self.config[ConfigKey.OPPONENT_COMMENTARY_TYPE] == ConfigValue.SPEAKER2:
            self.speak(self.config[ConfigKey.SPEAKER1][ConfigKey.CID], "?????????????????????????????????????????????", save=False)
            self.speak(self.config[ConfigKey.SPEAKER2][ConfigKey.CID], "???????????????????????????????????????????????????", save=False)
        elif self.config[ConfigKey.HERO_COMMENTARY_TYPE] == ConfigValue.SPEAKER1:
            self.speak(self.config[ConfigKey.SPEAKER1][ConfigKey.CID], "???????????????????????????????????????????????????", save=False)
        elif self.config[ConfigKey.OPPONENT_COMMENTARY_TYPE] == ConfigValue.SPEAKER1:
            self.speak(self.config[ConfigKey.SPEAKER1][ConfigKey.CID], "?????????????????????????????????????????????????????????", save=False)
        elif self.config[ConfigKey.OPPONENT_COMMENTARY_TYPE] == ConfigValue.SPEAKER2:
            self.speak(self.config[ConfigKey.SPEAKER2][ConfigKey.CID], "???????????????????????????????????????????????????", save=False)

    def run(self):
        self.logger.info("mtgatracker_backend.exe running check")
        running = False
        while not running:
            mtgatracker_backend = self.process_running_check(ProcessName.MTGATRACKER_BACKEND)
            running = True if mtgatracker_backend else False
            if not running:
                ans = messagebox.askyesno("mtgatracker_backend ????????????", "{} ????????????????????????????????????????????????\r\nmtgatracker_backend???????????????????????????????????????????????????\r\n??????: ?????????\r\n?????????: ??????????????????".format(ProcessName.MTGATRACKER_BACKEND))
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
                ans = messagebox.askyesno("AssistantSeika ????????????", "{} ????????????????????????????????????????????????\r\nAssistantSeika???????????????????????????????????????????????????\r\n??????: ?????????\r\n?????????: ??????????????????".format(ProcessName.ASSISTANT_SEIKA))
                if ans == True:
                    pass
                elif ans == False:
                    self.logger.info("AssistantSeika running check: NG")
                    self.no_assistant_seika = True
                    running = True
            else:
                self.logger.info("AssistantSeika running check: OK")

        if not self.no_assistant_seika:
            self.logger.info(ProcessName.SEIKA_SAY2+" existence check")
            running = False
            while not running:
                if os.path.exists(self.config.get(ConfigKey.SEIKA_SAY2_PATH)):
                    running = True
                else:
                    messagebox.showinfo(ProcessName.SEIKA_SAY2+" ????????????", "{} ????????????????????????????????????\r\n????????????????????????????????????????????????????????? {} ??????????????????????????????".format(ProcessName.SEIKA_SAY2, ProcessName.SEIKA_SAY2))
                    self.config[ConfigKey.SEIKA_SAY2_PATH] = filedialog.askopenfilename(filetype=[(ProcessName.SEIKA_SAY2,"*.exe")], initialdir=os.getcwd())
            self.seikasay2 = SeikaSay2(self.config.get(ConfigKey.SEIKA_SAY2_PATH))

            self.logger.info("Get speakers from AssistantSeika")
            running = False
            while not running:
                self.get_speaker_list()
                if self.cids:
                    running = True
                    self.logger.info("Get cids from AssistantSeika: OK")
                    break
                else:
                    ans = messagebox.askyesno("AssistantSeika ??????????????????", "AssistantSeika??????????????????????????????\r\n????????????????????????????????????AssistantSeika???????????????????????????????????????????????????????????????????????????????????????\r\n??????: ?????????\r\n?????????: ??????????????????")
                    if ans == True:
                        pass
                    elif ans == False:
                        self.logger.info("Get cids from AssistantSeika: NG")
                        running = True
        else:
            self.cids.append("0000")
            self.speakers.append("0000 ???????????????  - ????????????????????????????????? Neo?????????")

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
        self.logger.info("??????1: {}".format(self.config.get(ConfigKey.SPEAKER1).get(ConfigKey.NAME)))
        self.logger.info("??????2: {}".format(self.config.get(ConfigKey.SPEAKER2).get(ConfigKey.NAME)))
        self.speaker1_obj = self.load_speaker(self.config.get(ConfigKey.SPEAKER1).get(ConfigKey.CID))
        self.speaker2_obj = self.load_speaker(self.config.get(ConfigKey.SPEAKER2).get(ConfigKey.CID))

        self.start_ws_client()
        self.speak_config()

        self.master.mainloop()

        self.ws.close()

        #mtgatracker_backend?????????
        pid_list=[pc.pid for pc in mtgatracker_backend.children(recursive=True)] 
        for pid in pid_list:
            psutil.Process(pid).terminate()
            self.logger.debug("terminate ??????????????????{}" .format(pid))
        mtgatracker_backend.terminate()
        self.logger.debug("terminate  ??????????????????{}" .format(mtgatracker_backend.pid))

if __name__ == "__main__":
    #param = sys.argv
    root = tkinter.Tk()
    commentary_backend = CommentaryBackend(master=root)
    commentary_backend.run()
