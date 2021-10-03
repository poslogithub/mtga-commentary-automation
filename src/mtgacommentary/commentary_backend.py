import _thread
import json
import logging
import logging.handlers
import os
import psutil
import re
import sys
import tkinter
import websocket
from seikasay2 import SeikaSay2
from tkinter import filedialog, messagebox, ttk

class Key():
    # message from mtgatracker_backend
    GAME_HISTORY_EVENT = "game_history_event"
    TYPE = "type"
    TEXT = "text"

    # parsed
    IS_OPPONENT = "isOpponent"
    MESSAGE_TYPE = "messageType"
    VERB = "verb"
    ATTACKER = "attacker"
    BLOCKER = "blocker"
    CARD = "card"
    SOURCE = "source"
    REASON = "reason"
    LIFE_DIFF = "life_diff"
    LIFE_FROM = "life_from"
    LIFE_TO = "life_to"

    # config
    SEIKA_SAY2_PATH = "seikaSay2Path"
    SPEAKER1 = "speaker1"
    SPEAKER2 = "speaker2"
    CID = "cid"
    NAME = "name"
    HERO_COMMENTARY_TYPE = "heroCommentaryType"
    OPPONENT_COMMENTARY_TYPE = "opponentCommentaryType"
    MTGATRACKER_BACKEND_URL = "mtgatrackerBackendUrl"

    # speaker
    LIFE = "life"
    SPEAK = "speak"
    #TEXT = "text"  #reuse

    # speaker_param
    ASYNC = "async"
    VOLUME = "volume"
    SPEED = "speed"
    PITCH = "pitch"
    ALPHA = "alpha"
    INTONATION = "intonation"
    EMOTION_EP = "emotionEP"
    EMOTION_P = "emotionP"
    OVER_BANNER = "overBanner"

class Value():
    # message from mtgatracker_backend
    GAME = "game"
    TURN = "turn"
    HERO = "hero"
    OPPONENT = "opponent"

    # config
    SPEAKER1 = "speaker1"
    SPEAKER2 = "speaker2"
    NEVER = "never"

    #speaker
    SEIKA_SAY2 = "seikaSay2"
    GAIN = "gain"
    LOSE = "lose"

class Verb():
    # message from mtgatracker_backend
    ATTAKING = "attacking"
    BLOCKS = "blocks"
    CASTS ="casts"
    DRAWS = "draws"
    EXILES = "exiles"
    LIFE_TOTAL_CHANGED = "'s life total changed"
    PLAYS = "plays"
    RESOLVES = "resolves"
    SENT_TO_GRAVEYARD = "sent to graveyard"
    STARTING_HAND = "'s starting hand:"
    VS = "vs"

class Reason():
    # message from mtgatracker_backend
    CONJURE = "(Conjure)"
    DESTROY = "(Destroy)"
    DISCARD = "(Discard)"
    MILL = "(Mill)"
    PUT = "(Put)"
    SACRIFICE = "(Sacrifice)"
    SBA_DAMEGE  ="(SBA_Damage)"
    SBA_DEATHTOUCH = "(SBA_Deathtouch)",
    SBA_ZERO_TOUGHNESS = "(SBA_ZeroToughness)"
    SBA_UNATTACHED_AURA = "(SBA_UnattachedAura)"
    NIL = "(nil)"

class ProcessName():
    ASSISTANT_SEIKA = "AssistantSeika.exe"
    MTGATRACKER_BACKEND = "mtgatracker_backend.exe"
    SEIKA_SAY2 = "SeikaSay2.exe"

class CommentaryBackend:
    def __init__(self):
        self.CONFIG_FILE = "config\\config.json"
        self.DEFAULT_SPEAKER_FILE = "config\\defaultSpeaker.json"
        self.LOG_FILE = os.path.basename(__file__).split(".")[0]+".log"
        self.config = {
            Key.SEIKA_SAY2_PATH : ".\\"+ProcessName.SEIKA_SAY2,
            Key.SPEAKER1 : {
                Key.CID : 0,
                Key.NAME : ""
            },
            Key.SPEAKER2 : {
                Key.CID : 0,
                Key.NAME : ""
            },
            Key.HERO_COMMENTARY_TYPE : Value.SPEAKER1,
            Key.OPPONENT_COMMENTARY_TYPE : Value.SPEAKER1,
            Key.MTGATRACKER_BACKEND_URL : "ws://localhost:8089"
        }
        self.cids = []
        self.speakers = []
        self.speaker1_obj = {}
        self.speaker2_obj = {}
        self.hero_screen_name = ""
        self.opponent_screen_name = ""
        self.HERO_COMMENTARY_TYPES = ["話者1が一人称で実況する", "実況しない"]
        self.OPPONENT_COMMENTARY_TYPES = ["話者1が三人称で実況する", "話者2が一人称で実況する", "実況しない"]

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

        self.logger.info("Loading {}".format(self.CONFIG_FILE))
        if self.load_config():
            self.logger.info("Loading {}: OK".format(self.CONFIG_FILE))
        else:
            self.logger.info("Loading {}: NG".format(self.CONFIG_FILE))
        self.seikasay2 = SeikaSay2(self.config.get(Key.SEIKA_SAY2_PATH))
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp(self.config.get(Key.MTGATRACKER_BACKEND_URL),
            on_open = self.on_open,
            on_message = self.on_message,
            on_error = self.on_error,
            on_close = self.on_close)
        self.window = tkinter.Tk()
        self.window.withdraw()

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
        speaker1_index = self.cids.index(self.config.get(Key.SPEAKER1).get(Key.CID))
        speaker2_index = self.cids.index(self.config.get(Key.SPEAKER2).get(Key.CID))

        self.window.title("MTGA自動実況ツール")
        self.window.geometry("480x240")
        self.window.deiconify()
        self.frame = ttk.Frame(self.window)
        self.frame.grid(column=0, row=0, sticky=tkinter.NSEW, padx=5, pady=10)
        self.sv_seikasay2_path = tkinter.StringVar()
        self.sv_seikasay2_path.set(self.config.get(Key.SEIKA_SAY2_PATH))
        self.sv_speaker1 = tkinter.StringVar()
        self.sv_speaker2 = tkinter.StringVar()
        self.sv_hero_commentary_type = tkinter.StringVar()
        self.sv_opponent_commentary_type = tkinter.StringVar()
        label_seikasay2 = ttk.Label(self.frame, text="SeikaSay2のパス: ", anchor="w")
        label_seikasay2.grid(row=0, column=0, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        entry_seikasay2 = ttk.Entry(self.frame, width=40, textvariable=self.sv_seikasay2_path)
        entry_seikasay2.grid(row=0, column=1, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        button_seikasay2 = tkinter.Button(self.frame, text="参照", command=self.config_window_seikasay2)
        button_seikasay2.grid(row=0, column=2, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        label_speaker1 = ttk.Label(self.frame, text="話者1: ", anchor="w")
        label_speaker1.grid(row=1, column=0, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        combobox_speaker1 = ttk.Combobox(self.frame, width=40, values=self.speakers, textvariable=self.sv_speaker1, state="readonly")
        combobox_speaker1.current(speaker1_index)
        combobox_speaker1.grid(row=1, column=1, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        label_speaker2 = ttk.Label(self.frame, text="話者2: ", anchor="w")
        label_speaker2.grid(row=2, column=0, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        combobox_speaker2 = ttk.Combobox(self.frame, width=40, values=self.speakers, textvariable=self.sv_speaker2, state="readonly")
        combobox_speaker2.current(speaker2_index)
        combobox_speaker2.grid(row=2, column=1, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        label_hero_commentary_type = ttk.Label(self.frame, text="自分のアクション: ", anchor="w")
        label_hero_commentary_type.grid(row=3, column=0, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        combobox_hero_commentary_type = ttk.Combobox(self.frame, width=40, values=self.HERO_COMMENTARY_TYPES, textvariable=self.sv_hero_commentary_type, state="readonly")
        combobox_hero_commentary_type.current(0 if self.config.get(Key.HERO_COMMENTARY_TYPE) == Value.SPEAKER1 else 1)
        combobox_hero_commentary_type.grid(row=3, column=1, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        label_opponent_commentary_type = ttk.Label(self.frame, text="対戦相手のアクション: ", anchor="w")
        label_opponent_commentary_type.grid(row=4, column=0, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        combobox_opponent_commentary_type = ttk.Combobox(self.frame, width=40, values=self.OPPONENT_COMMENTARY_TYPES, textvariable=self.sv_opponent_commentary_type, state="readonly")
        combobox_opponent_commentary_type.current(0 if self.config.get(Key.OPPONENT_COMMENTARY_TYPE) == Value.SPEAKER1 else 1 if self.config.get(Key.OPPONENT_COMMENTARY_TYPE) == Value.SPEAKER2 else 2)
        combobox_opponent_commentary_type.grid(row=4, column=1, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        button_ok = tkinter.Button(self.frame, text="OK", command=self.config_window_ok)
        button_ok.grid(row=5, column=1, sticky=tkinter.E, padx=5, pady=5)
        button_cancel = tkinter.Button(self.frame, text="キャンセル", command=self.config_window_cancel)
        button_cancel.grid(row=5, column=2, sticky=tkinter.W + tkinter.E, padx=5, pady=5)
        self.window.mainloop()
    
    def config_window_seikasay2(self):
        path = filedialog.askopenfilename(filetype=[("実行ファイル","*.exe")], initialdir=os.getcwd())
        self.sv_seikasay2_path.set(path)

    def config_window_ok(self):
        self.config[Key.SEIKA_SAY2_PATH] = self.sv_seikasay2_path.get()
        self.config[Key.SPEAKER1][Key.CID] = int(self.sv_speaker1.get().split(" ")[0])
        self.config[Key.SPEAKER1][Key.NAME] = self.sv_speaker1.get()
        self.config[Key.SPEAKER2][Key.CID] = int(self.sv_speaker2.get().split(" ")[0])
        self.config[Key.SPEAKER2][Key.NAME] = self.sv_speaker2.get()
        self.config[Key.HERO_COMMENTARY_TYPE] = \
            Value.SPEAKER1 if self.sv_hero_commentary_type.get() == self.HERO_COMMENTARY_TYPES[0] \
            else Value.NEVER
        self.config[Key.OPPONENT_COMMENTARY_TYPE] = \
            Value.SPEAKER1 if self.sv_opponent_commentary_type.get() == self.OPPONENT_COMMENTARY_TYPES[0] \
            else Value.SPEAKER2 if self.sv_opponent_commentary_type.get() == self.OPPONENT_COMMENTARY_TYPES[1] \
            else Value.NEVER
        self.save_config()
        self.window.withdraw()
        self.window.destroy()

    def config_window_cancel(self):
        self.window.withdraw()
        self.window.destroy()

    def load_speaker(self, cid):
        speaker_file = "config\\{}.json".format(cid)
        if not os.path.isfile(speaker_file):
            speaker_file = self.DEFAULT_SPEAKER_FILE
        with open(speaker_file, 'r', encoding="utf_8_sig") as rf:
            return json.load(rf)

    def load_speakers(self):
        speaker_file = "config\\{}.json".format(self.config.get(Key.SPEAKER1).get(Key.CID))
        if not os.path.isfile(speaker_file):
            speaker_file = self.DEFAULT_SPEAKER_FILE
        with open(speaker_file, 'r', encoding="utf_8_sig") as rf:
            self.speaker1_obj = json.load(rf)

        speaker_file = "config\\{}.json".format(self.config.get(Key.SPEAKER2).get(Key.CID))
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
        if blob and Key.GAME_HISTORY_EVENT in blob:
            text_array = blob.get(Key.GAME_HISTORY_EVENT)
            parsed = {}

            if len(text_array) == 0:
                self.logger.warning("warning: 長さ0のtext_array")
            elif len(text_array) == 1:
                if text_array[0].get(Key.TYPE) == Value.GAME:
                    parsed[Key.MESSAGE_TYPE] = text_array[0].get(Key.TYPE)
                elif text_array[0].get(Key.TYPE) == Value.TURN:
                    if text_array[0].get(Key.TEXT).find(self.opponent_screen_name) >= 0:
                        parsed[Key.IS_OPPONENT] = True
                    parsed[Key.MESSAGE_TYPE] = text_array[0].get(Key.TYPE)
                else:
                    self.logger.warning("warning: 不明なtype: {}".format(text_array[0].get(Key.TYPE)))
            else:
                parsed[Key.VERB] = text_array[1].strip()
                if parsed.get(Key.VERB) == "'s":    # "'s"が入った場合はガチャガチャする
                    parsed[Key.SOURCE] = text_array[0].get(Key.TEXT)
                    parsed[Key.IS_OPPONENT] = True if text_array[0].get(Key.TYPE) == Value.OPPONENT else False
                    parsed[Key.MESSAGE_TYPE] = text_array[2].get(Key.TYPE)    # ability
                    if len(text_array) >= 4 and text_array[3].strip() != ":":   # ex: "CARDNAME1 's ability exiles CARDNAME2"
                        text_array = text_array[2:]
                    elif len(text_array) >= 6 and text_array[3].strip() == ":": # ex: "CARDNAME1 's ability : SCREENNAME draws CARDNAME2"
                        text_array = text_array[4:]
                    parsed[Key.VERB] = text_array[1].strip()
                    if parsed.get(Key.VERB) == "'s":
                        self.logger.warning("warning: 不明なtext_array: {}".format(text_array))

                if parsed.get(Key.VERB) == ":":    # ":"が入った場合はガチャガチャする
                    parsed[Key.SOURCE] = text_array[0].get(Key.TEXT)
                    if len(text_array) >= 4:   # ex: "CARDNAME1 : SCREENNAME draws CARDNAME2"
                        text_array = text_array[2:]
                    parsed[Key.VERB] = text_array[1].strip()
                    if parsed.get(Key.VERB) == ":":
                        self.logger.warning("warning: 不明なtext_array: {}".format(text_array))

                if parsed.get(Key.VERB) == Verb.ATTAKING:
                    parsed[Key.IS_OPPONENT] = True if text_array[0].get(Key.TYPE) == Value.OPPONENT else False
                    parsed[Key.ATTACKER] = self.del_ruby(text_array[0].get(Key.TEXT))
                elif parsed.get(Key.VERB) == Verb.BLOCKS:
                    parsed[Key.IS_OPPONENT] = True if text_array[0].get(Key.TYPE) == Value.OPPONENT else False
                    parsed[Key.BLOCKER] = self.del_ruby(text_array[0].get(Key.TEXT))
                    parsed[Key.ATTACKER] = self.del_ruby(text_array[2].get(Key.TEXT))
                elif parsed.get(Key.VERB) == Verb.CASTS:
                    parsed[Key.IS_OPPONENT] = True if text_array[0].get(Key.TYPE) == Value.OPPONENT else False
                    parsed[Key.CARD] = self.del_ruby(text_array[2].get(Key.TEXT))
                elif parsed.get(Key.VERB) == Verb.DRAWS:
                    parsed[Key.IS_OPPONENT] = True if text_array[0].get(Key.TYPE) == Value.OPPONENT else False
                    if len(text_array) >= 3:
                        parsed[Key.CARD] = self.del_ruby(text_array[2].get(Key.TEXT))
                elif parsed.get(Key.VERB) == Verb.EXILES:
                    parsed[Key.IS_OPPONENT] = True if text_array[2].get(Key.TYPE) == Value.OPPONENT else False
                    parsed[Key.CARD] = self.del_ruby(text_array[2].get(Key.TEXT))
                elif parsed.get(Key.VERB) == Verb.LIFE_TOTAL_CHANGED:
                    parsed[Key.IS_OPPONENT] = True if text_array[0].get(Key.TYPE) == Value.OPPONENT else False
                    parsed[Key.LIFE_FROM] = int(text_array[2].split(" -> ")[0])
                    parsed[Key.LIFE_TO] = int(text_array[2].split(" -> ")[1])
                    parsed[Key.LIFE_DIFF] = parsed[Key.LIFE_TO] - parsed[Key.LIFE_FROM]
                elif parsed.get(Key.VERB) == Verb.PLAYS:
                    parsed[Key.IS_OPPONENT] = True if text_array[0].get(Key.TYPE) == Value.OPPONENT else False
                    parsed[Key.CARD] = self.del_ruby(text_array[2].get(Key.TEXT))
                elif parsed.get(Key.VERB) == Verb.RESOLVES:
                    parsed[Key.IS_OPPONENT] = True if text_array[0].get(Key.TYPE) == Value.OPPONENT else False
                    parsed[Key.CARD] = self.del_ruby(text_array[0].get(Key.TEXT))
                elif parsed.get(Key.VERB) == Verb.SENT_TO_GRAVEYARD:
                    parsed[Key.IS_OPPONENT] = True if text_array[0].get(Key.TYPE) == Value.OPPONENT else False
                    parsed[Key.CARD] = self.del_ruby(text_array[0].get(Key.TEXT))
                    parsed[Key.REASON] = text_array[2]
                    if parsed.get(Key.REASON) not in [
                        Reason.CONJURE,
                        Reason.DESTROY,
                        Reason.DISCARD,
                        Reason.MILL,
                        Reason.PUT,
                        Reason.SACRIFICE,
                        Reason.SBA_DAMEGE,
                        Reason.SBA_DEATHTOUCH,
                        Reason.SBA_ZERO_TOUGHNESS,
                        Reason.SBA_UNATTACHED_AURA,
                        Reason.NIL
                    ]:
                        self.logger.warning("warning: 不明なreason: {}".format(parsed.get(Key.REASON)))
                elif parsed.get(Key.VERB) == Verb.STARTING_HAND:
                    pass
                elif parsed.get(Key.VERB) == Verb.VS:
                    self.hero_screen_name = text_array[0].get(Key.TEXT)
                    self.opponent_screen_name = text_array[2].get(Key.TEXT)
                else:
                    self.logger.warning("warning: 不明なverb: ".format(parsed.get(Key.VERB)))

            return parsed
        else:
            return None

    def gen_text(self, parsed):
        if not parsed.get(Key.IS_OPPONENT):
            if self.config.get(Key.HERO_COMMENTARY_TYPE) == Value.SPEAKER1:
                cid = self.config.get(Key.SPEAKER1).get(Key.CID)
                speaker = self.speaker1_obj
                speak_idx = 0
            else:
                return None
        else:
            if self.config.get(Key.OPPONENT_COMMENTARY_TYPE) == Value.SPEAKER1:
                cid = self.config.get(Key.SPEAKER1).get(Key.CID)
                speaker = self.speaker1_obj
                speak_idx = 1
            elif self.config.get(Key.OPPONENT_COMMENTARY_TYPE) == Value.SPEAKER2:
                cid = self.config.get(Key.SPEAKER2).get(Key.CID)
                speaker = self.speaker2_obj
                speak_idx = 2
            else:
                return None
        
        speak_obj = None
        if parsed.get(Key.MESSAGE_TYPE) in [Value.GAME, Value.TURN]:
            for obj in speaker:
                if obj.get(Key.TYPE) == parsed.get(Key.MESSAGE_TYPE):
                    speak_obj = obj.get(Key.SPEAK)[speak_idx]
                    break
        else:
            for obj in speaker:
                if obj.get(Key.VERB) == parsed.get(Key.VERB):
                    if obj.get(Key.VERB) == Verb.SENT_TO_GRAVEYARD:
                        if parsed.get(Key.REASON) not in obj.get(Key.REASON):
                            continue
                    if obj.get(Key.VERB) == Verb.LIFE_TOTAL_CHANGED:
                        if obj.get(Key.LIFE) == Value.GAIN and parsed.get(Key.LIFE_DIFF) < 0:
                            continue
                        if obj.get(Key.LIFE) == Value.LOSE and parsed.get(Key.LIFE_DIFF) > 0:
                            continue
                        parsed[Key.LIFE_DIFF] = abs(parsed.get(Key.LIFE_DIFF))
                    speak_obj = obj.get(Key.SPEAK)[speak_idx]
                    break
        
        text = speak_obj.get(Key.TEXT) \
            .replace("{"+Key.ATTACKER+"}", parsed.get(Key.ATTACKER) if parsed.get(Key.ATTACKER) else "") \
            .replace("{"+Key.BLOCKER+"}", parsed.get(Key.BLOCKER) if parsed.get(Key.BLOCKER) else "") \
            .replace("{"+Key.CARD+"}", parsed.get(Key.CARD) if parsed.get(Key.CARD) else "") \
            .replace("{"+Key.SOURCE+"}", parsed.get(Key.SOURCE) if parsed.get(Key.SOURCE) else "") \
            .replace("{"+Key.LIFE_FROM+"}", str(parsed.get(Key.LIFE_FROM)) if str(parsed.get(Key.LIFE_FROM)) else "") \
            .replace("{"+Key.LIFE_TO+"}", str(parsed.get(Key.LIFE_TO)) if str(parsed.get(Key.LIFE_TO)) else "") \
            .replace("{"+Key.LIFE_DIFF+"}", str(parsed.get(Key.LIFE_DIFF)) if str(parsed.get(Key.LIFE_DIFF)) else "")

        speak_param_obj = {}
        for obj in speaker:
            if obj.get(Key.TYPE) == Value.SEIKA_SAY2:
                speak_param_obj = obj
                break
        if not speak_param_obj:
            speak_param_obj[Key.ASYNC] = speak_obj.get(Key.ASYNC) if speak_obj.get(Key.ASYNC) else speak_param_obj.get(Key.ASYNC)
            speak_param_obj[Key.VOLUME] = speak_obj.get(Key.VOLUME) if speak_obj.get(Key.VOLUME) else speak_param_obj.get(Key.VOLUME)
            speak_param_obj[Key.SPEED] = speak_obj.get(Key.SPEED) if speak_obj.get(Key.SPEED) else speak_param_obj.get(Key.SPEED)
            speak_param_obj[Key.PITCH] = speak_obj.get(Key.PITCH) if speak_obj.get(Key.PITCH) else speak_param_obj.get(Key.PITCH)
            speak_param_obj[Key.ALPHA] = speak_obj.get(Key.ALPHA) if speak_obj.get(Key.ALPHA) else speak_param_obj.get(Key.ALPHA)
            speak_param_obj[Key.INTONATION] = speak_obj.get(Key.INTONATION) if speak_obj.get(Key.INTONATION) else speak_param_obj.get(Key.INTONATION)
            speak_param_obj[Key.EMOTION_EP] = speak_obj.get(Key.EMOTION_EP) if speak_obj.get(Key.EMOTION_EP) else speak_param_obj.get(Key.EMOTION_EP)
            speak_param_obj[Key.EMOTION_P] = speak_obj.get(Key.EMOTION_P) if speak_obj.get(Key.EMOTION_P) else speak_param_obj.get(Key.EMOTION_P)
            speak_param_obj[Key.OVER_BANNER] = speak_obj.get(Key.OVER_BANNER) if speak_obj.get(Key.OVER_BANNER) else speak_param_obj.get(Key.OVER_BANNER)
        else:
            speak_param_obj[Key.ASYNC] = speak_obj.get(Key.ASYNC)
            speak_param_obj[Key.VOLUME] = speak_obj.get(Key.VOLUME)
            speak_param_obj[Key.SPEED] = speak_obj.get(Key.SPEED)
            speak_param_obj[Key.PITCH] = speak_obj.get(Key.PITCH)
            speak_param_obj[Key.ALPHA] = speak_obj.get(Key.ALPHA)
            speak_param_obj[Key.INTONATION] = speak_obj.get(Key.INTONATION)
            speak_param_obj[Key.EMOTION_EP] = speak_obj.get(Key.EMOTION_EP)
            speak_param_obj[Key.EMOTION_P] = speak_obj.get(Key.EMOTION_P)
            speak_param_obj[Key.OVER_BANNER] = speak_obj.get(Key.OVER_BANNER)

        return cid, text, speak_param_obj

    def get_speaker_list(self):
        self.cids, self.speakers = self.seikasay2.list()
        return self.cids, self.speakers
    
    def speak(self, cid, text, speak_param_obj={}):
        if cid and text:
            speaked_text = self.seikasay2.speak( \
                cid=cid, \
                text=text, \
                asynchronize=speak_param_obj.get(Key.ASYNC), \
                volume=speak_param_obj.get(Key.VOLUME), \
                speed=speak_param_obj.get(Key.SPEED), \
                pitch=speak_param_obj.get(Key.PITCH), \
                alpha=speak_param_obj.get(Key.ALPHA), \
                intonation=speak_param_obj.get(Key.INTONATION), \
                emotionEP=speak_param_obj.get(Key.EMOTION_EP), \
                emotionP=speak_param_obj.get(Key.EMOTION_P), \
                overBanner=speak_param_obj.get(Key.OVER_BANNER) \
            )
            return speaked_text
        else:
            return None

    def on_message(self, ws, message):
        parsed = self.parse(json.loads(message))
        self.logger.debug(parsed)
        cid = 0
        text = ""
        speak_param_obj = {}
        if parsed:
            cid, text, speak_param_obj = self.gen_text(parsed)
        if cid and text:
            speaked_text = self.speak(cid, text, speak_param_obj)
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
        if self.config[Key.HERO_COMMENTARY_TYPE] == Value.SPEAKER1 and self.config[Key.OPPONENT_COMMENTARY_TYPE] == Value.SPEAKER1:
            self.speak(self.config[Key.SPEAKER1][Key.CID], "自分と対戦相手のアクションを実況します。")
        elif self.config[Key.HERO_COMMENTARY_TYPE] == Value.SPEAKER1 and self.config[Key.OPPONENT_COMMENTARY_TYPE] == Value.SPEAKER2:
            self.speak(self.config[Key.SPEAKER1][Key.CID], "自分のアクションを実況します。")
            self.speak(self.config[Key.SPEAKER2][Key.CID], "対戦相手のアクションを実況します。")
        elif self.config[Key.HERO_COMMENTARY_TYPE] == Value.SPEAKER1:
            self.speak(self.config[Key.SPEAKER1][Key.CID], "自分のアクションだけを実況します。")
        elif self.config[Key.OPPONENT_COMMENTARY_TYPE] == Value.SPEAKER1:
            self.speak(self.config[Key.SPEAKER1][Key.CID], "対戦相手のアクションだけを実況します。")
        elif self.config[Key.OPPONENT_COMMENTARY_TYPE] == Value.SPEAKER2:
            self.speak(self.config[Key.SPEAKER2][Key.CID], "対戦相手のアクションを実況します。")

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

        if not self.config.get(Key.SPEAKER1).get(Key.CID):
            self.config[Key.SPEAKER1][Key.CID] = self.cids[0]
        if not self.config.get(Key.SPEAKER2).get(Key.CID):
            self.config[Key.SPEAKER2][Key.CID] = \
                self.cids[1] if len(self.cids) >= 2 \
                else self.cids[0]

        self.open_config_window()
        self.logger.info("話者1: {}".format(self.config.get(Key.SPEAKER1).get(Key.NAME)))
        self.logger.info("話者2: {}".format(self.config.get(Key.SPEAKER2).get(Key.NAME)))
        self.load_speakers()
        self.speak_config()
        
        try:
            self.ws.run_forever()
        except KeyboardInterrupt:
            self.ws.close()

if __name__ == "__main__":
    #param = sys.argv
    commentary_backend = CommentaryBackend()
    commentary_backend.run()
