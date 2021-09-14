import _thread
import json
import re
import sys
import websocket
from seikasay2 import SeikaSay2
import logging
from logging import getLogger, StreamHandler
import logging.handlers
import os
import psutil
from tkinter import Tk, messagebox


seikasay2 = SeikaSay2()
hero_screen_name = ""
opponent_screen_name = ""

def on_message(ws, message):
    global hero_screen_name
    global opponent_screen_name

    blob = json.loads(message)
    logger.debug(blob)
    if blob and "game_history_event" in blob:
        text_array = blob.get("game_history_event")
        is_opponent = False
        message_type = ""
        verb = ""
        attacker = ""
        blocker = ""
        card = ""
        source = ""
        reason = ""
        life_from = 0
        life_to = 0

        if len(text_array) == 0:
            logger.warning("warning: 長さ0のtext_array")
        elif len(text_array) == 1:
            if text_array[0].get("type") == "game":
                message_type = text_array[0].get("type")
            elif text_array[0].get("type") == "turn":
                if text_array[0].get("text").find(opponent_screen_name) >= 0:
                    is_opponent = True
                message_type = text_array[0].get("type")
            else:
                logger.warning("warning: 不明なtype: {}".format(text_array[0].get("type")))
        else:
            verb = text_array[1].strip()
            if verb == "'s":    # "'s"が入った場合はガチャガチャする
                source = text_array[0].get("text")
                is_opponent = True if text_array[0].get("type") == "opponent" else False
                message_type = text_array[2].get("type")    # ability
                if len(text_array) >= 4 and text_array[3].strip() != ":":   # ex: "CARDNAME1 's ability exiles CARDNAME2"
                    text_array = text_array[2:]
                elif len(text_array) >= 6 and text_array[3].strip() == ":": # ex: "CARDNAME1 's ability : SCREENNAME draws CARDNAME2"
                    text_array = text_array[4:]
                verb = text_array[1].strip()
                if verb == "'s":
                    logger.warning("warning: 不明なtext_array: {}".format(text_array))

            if verb == ":":    # ":"が入った場合はガチャガチャする
                source = text_array[0].get("text")
                if len(text_array) >= 4:   # ex: "CARDNAME1 : SCREENNAME draws CARDNAME2"
                    text_array = text_array[2:]
                verb = text_array[1].strip()
                if verb == ":":
                    logger.warning("warning: 不明なtext_array: {}".format(text_array))

            if verb == "attacking":
                is_opponent = True if text_array[0].get("type") == "opponent" else False
                attacker = re.sub("（.+?）", "", text_array[0].get("text"))
            elif verb == "blocks":
                is_opponent = True if text_array[0].get("type") == "opponent" else False
                blocker = re.sub("（.+?）", "", text_array[0].get("text"))
                attacker = re.sub("（.+?）", "", text_array[2].get("text"))
            elif verb == "casts":
                is_opponent = True if text_array[0].get("type") == "opponent" else False
                card = re.sub("（.+?）", "", text_array[2].get("text"))
            elif verb == "draws":
                is_opponent = True if text_array[0].get("type") == "opponent" else False
                if len(text_array) >= 3:
                    card = re.sub("（.+?）", "", text_array[2].get("text"))
            elif verb == "exiles":
                is_opponent = True if text_array[2].get("type") == "opponent" else False
                card = re.sub("（.+?）", "", text_array[2].get("text"))
            elif verb == "plays":
                is_opponent = True if text_array[0].get("type") == "opponent" else False
                card = re.sub("（.+?）", "", text_array[2].get("text"))
            elif verb == "resolves":
                is_opponent = True if text_array[0].get("type") == "opponent" else False
                card = re.sub("（.+?）", "", text_array[0].get("text"))
            elif verb == "sent to graveyard":
                is_opponent = True if text_array[0].get("type") == "opponent" else False
                card = re.sub("（.+?）", "", text_array[0].get("text"))
                reason = text_array[2]
                if reason not in ["(Conjure)", "(Destroy)", "(Discard)", "(Mill)", "(Sacrifice)", "(SBA_Damage)", "(SBA_ZeroToughness)", "(SBA_UnattachedAura)", "(nil)"]:
                    logger.warning("warning: 不明なreason: {}".format(reason))
            elif verb == "vs":
                hero_screen_name = text_array[0].get("text")
                opponent_screen_name = text_array[2].get("text")
            elif verb == "'s life total changed":
                is_opponent = True if text_array[0].get("type") == "opponent" else False
                life_from = int(text_array[2].split(" -> ")[0])
                life_to = int(text_array[2].split(" -> ")[1])
            elif verb == "'s starting hand:":
                pass
            else:
                logger.warning("warning: 不明なverb: ".format(verb))

        text = seikasay2.speak(is_opponent, message_type, verb, attacker, blocker, card, source, reason, life_from, life_to)
        if text:
            logger.info(text)

def on_error(ws, error):
    logger.error("error: called on_error")
    logger.error(error)

def on_close(ws):
    logger.info("### websocket is closed ###")

def on_open(ws):
    def run(*args):
        logger.info("### websocket is opened ###")

        while(True):
            line = sys.stdin.readline()
            if line != "":
                logger.debug("debug: sending value is " + line)
                ws.send(line)

    _thread.start_new_thread(run, ())


if __name__ == "__main__":
    log_file = "commentary_backend.log"
    logger = getLogger("commentary_backend")
    logger.setLevel(logging.DEBUG)
    stream_handler = StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    must_rollover = False
    if os.path.exists(log_file):  # check before creating the handler, which creates the file
        must_rollover = True
    rotating_handler = logging.handlers.RotatingFileHandler(log_file, backupCount=10)
    rotating_handler.setLevel(logging.DEBUG)
    if must_rollover:
        try:
            rotating_handler.doRollover()
        except PermissionError:
            print("警告: {} のローテーションに失敗しました。ログファイルが出力されません。".format(log_file))
    logger.addHandler(stream_handler)
    logger.addHandler(rotating_handler)

    param = sys.argv

    url = "ws://localhost:8089"

    if len(param) == 2:
        url = param[1]
        logger.info("param[1] is " + param[1])

    root = Tk()
    root.withdraw()

    logger.info("mtgatracker_backend.exe running check")
    running = False
    while not running:
        for proc in psutil.process_iter():
            try:
                if proc.exe().endswith("mtgatracker_backend.exe"):
                    logger.info("mtgatracker_backend.exe running check: OK")
                    running = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        if not running:
            ans = messagebox.askyesno(__file__, "mtgatracker_backend.exe プロセスが見つかりませんでした。\nmtgatracker_backendが起動していない可能性があります。\nはい: 再試行\nいいえ: 無視して続行")
            if ans == True:
                pass
            elif ans == False:
                logger.infoint("mtgatracker_backend.exe running check: NG")
                running = True

    logger.info("AssistantSeika running check")
    running = False
    while not running:
        for proc in psutil.process_iter():
            try:
                if proc.exe().endswith("AssistantSeika.exe"):
                    logger.info("AssistantSeika running check: OK")
                    running = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        if not running:
            ans = messagebox.askyesno(__file__, "AssistantSeika.exe プロセスが見つかりませんでした。\nAssistantSeikaが起動していない可能性があります。\nはい: 再試行\nいいえ: 無視して続行")
            if ans == True:
                pass
            elif ans == False:
                logger.info("AssistantSeika running check: NG")
                running = True

    logger.info("Get cids from AssistantSeika")
    running = False
    while not running:
        cids = seikasay2.cid_list()
        if cids:
            running = True
            logger.info("Get cids from AssistantSeika: OK")
            break
        else:
            ans = messagebox.askyesno(__file__, "SeikaSay2.exe -list の実行に失敗しました。\nAssistantSeikaの話者一覧が空である可能性があります。\nはい: 再試行\nいいえ: 無視して続行")
            if ans == True:
                pass
            elif ans == False:
                logger.info("Get cids from AssistantSeika: NG")
                running = True
    
    seikasay2.set_cids(cids[0], cids[1] if len(cids) >= 2 else cids[0])
    logger.info("hero_cid: {}".format(seikasay2.hero_cid))
    logger.info("opponent_cid: {}".format(seikasay2.opponent_cid))

    seikasay2.speak_config()
    
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(url,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()