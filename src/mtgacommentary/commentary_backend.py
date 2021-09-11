import _thread
import json
import re
import sys
import time
import websocket
from seikasay2 import SeikaSay2
from logging import getLogger
import psutil
from tkinter import Tk, messagebox
import subprocess


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
            logger.warning("debug: 不明なtext_array")
        elif len(text_array) == 1:
            if text_array[0].get("type") == "game":
                message_type = text_array[0].get("type")
            elif text_array[0].get("type") == "turn":
                if text_array[0].get("text").find(opponent_screen_name) >= 0:
                    is_opponent = True
                message_type = text_array[0].get("type")
            else:
                logger.warning("debug: 不明なtype")
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
                    logger.warning("debug: 不明なverb")

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
                if reason not in ["(Conjure)", "(Destroy)", "(Discard)", "(Sacrifice)", "(SBA_Damage)", "(SBA_ZeroToughness)", "(SBA_UnattachedAura)", "(nil)"]:
                    logger.warning("debug: 不明なreason")
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
                logger.warning("debug: 不明なverb")

        text = seikasay2.speak(is_opponent, message_type, verb, attacker, blocker, card, source, reason, life_from, life_to)
        if text:
            print(text)
            logger.info(text)

def on_error(ws, error):
    print(error)
    logger.error("debug: called on_error")
    logger.error(error)

def on_close(ws):
    print("### closed ###")
    logger.info("### closed ###")

def on_open(ws):
    def run(*args):
        print("### websocket is opened ###")
        logger.info("debug: websocket is opened")

        while(True):
            line = sys.stdin.readline()
            if line != "":
                print("sending value is " + line)
                logger.info("debug: sending value is " + line)
                ws.send(line)

    _thread.start_new_thread(run, ())


if __name__ == "__main__":
    logger = getLogger("commentary_backend")
    param = sys.argv

    url = "ws://localhost:8089"

    if len(param) == 2:
        url = param[1]
        print("param[1] is " + param[1])
        logger.info("debug: param[1] is " + param[1])

    root = Tk()
    root.withdraw()

    print("mtgatracker_backend.exe running check")
    running = False
    while not running:
        for proc in psutil.process_iter():
            try:
                if proc.exe().endswith("mtgatracker_backend.exe"):
                    print("mtgatracker_backend.exe running check: OK")
                    running = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        if not running:
            ans = messagebox.askyesno(__file__, "mtgatracker_backend.exe プロセスが見つかりませんでした。\nmtgatracker_backendが起動していない可能性があります。\nはい: 再試行\nいいえ: 無視して続行")
            if ans == True:
                pass
            elif ans == False:
                print("mtgatracker_backend.exe running check: NG")
                running = True

    print("AssistantSeika running check")
    running = False
    while not running:
        for proc in psutil.process_iter():
            try:
                if proc.exe().endswith("AssistantSeika.exe"):
                    print("AssistantSeika running check: OK")
                    running = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        if not running:
            ans = messagebox.askyesno(__file__, "AssistantSeika.exe プロセスが見つかりませんでした。\nAssistantSeikaが起動していない可能性があります。\nはい: 再試行\nいいえ: 無視して続行")
            if ans == True:
                pass
            elif ans == False:
                print("AssistantSeika running check: NG")
                running = True

    print("Get cids from AssistantSeika")
    running = False
    while not running:
        cids = seikasay2.cid_list()
        if cids:
            running = True
            print("Get cids from AssistantSeika: OK")
            break
        else:
            ans = messagebox.askyesno(__file__, "SeikaSay2.exe -list の実行に失敗しました。\nAssistantSeikaの話者一覧が空である可能性があります。\nはい: 再試行\nいいえ: 無視して続行")
            if ans == True:
                pass
            elif ans == False:
                print("Get cids from AssistantSeika: NG")
                running = True
    
    seikasay2.set_cids(cids[0], cids[1] if len(cids) >= 2 else cids[0])
    print("hero_cid: {}".format(seikasay2.hero_cid))
    print("opponent_cid: {}".format(seikasay2.opponent_cid))

    seikasay2.speak_config()
    
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(url,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()