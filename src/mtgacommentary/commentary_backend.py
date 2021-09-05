import _thread
import json
import re
import sys
import time
import websocket
from seikasay2 import SeikaSay2

seikasey2 = SeikaSay2()

def on_message(ws, message):
    print(json.dumps(message, ensure_ascii=False))  #debug
    text = ""
    blob = json.loads(message)
    if blob and "game_history_event" in blob:
        verb = ""
        is_opponent = False
        text_array = blob.get("game_history_event")
        if len(text_array) >= 1:
            actor_text = ""
            if isinstance(text_array[0], dict):
                actor_text = re.sub("（.+?）", "", text_array[0].get("text"))
                if text_array[0].get("type") == "opponent":
                    is_opponent = True
                elif text_array[0].get("type") == "game":
                    text = "対戦ありがとうございました。"
            else:
                actor_text = re.sub("（.+?）", "", text_array[0])
        if len(text_array) >= 2:
            verb = text_array[1]
        if verb == " attacking":
            text = "{}{}でアタック。".format("お相手は" if is_opponent else "", actor_text)
        if len(text_array) >= 3:
            target_text = ""
            if isinstance(text_array[2], dict):
                target_text = re.sub("（.+?）", "", text_array[2].get("text"))
            else:
                target_text = re.sub("（.+?）", "", text_array[2])
            if verb == " vs ":
                text = "おっすおねがいしまーす。"
            elif verb == " draws " and not is_opponent:
                text = "{}をドロー。".format(target_text)
            elif verb == " plays ":
                text = "{}{}をプレイ。".format("お相手は" if is_opponent else "", target_text)
            elif verb == " casts ":
                text = "{}{}をキャスト。".format("お相手は" if is_opponent else "", target_text)
            elif verb == " blocks ":
                text = "{}{}で{}をブロック。".format("お相手は" if is_opponent else "", actor_text, target_text)
            # elif verb == " sent to graveyard ":
            #     text = "{}{}が墓地に。".format("お相手の" if is_opponent else "", actor_text))
            elif verb == "'s life total changed ":
                life_from = int(target_text.split(" -> ")[0])
                life_to = int(target_text.split(" -> ")[1])
                if not is_opponent and life_from > life_to:
                    text = "{}点くらって、ライフは{}。".format(life_from - life_to, life_to)
                elif not is_opponent and life_from < life_to:
                    text = "{}点回復して、ライフは{}。".format(life_to - life_from, life_to)
                elif not is_opponent and life_from > life_to:
                    text = "{}点あたえて、お相手のライフは{}。".format(life_from - life_to, life_to)
                elif not is_opponent and life_from < life_to:
                    text = "{}点回復されて、お相手のライフは{}。".format(life_to - life_from, life_to)
            # elif verb == "'s ":
            #     text = "{}{}の能力を起動。".format("お相手は" if is_opponent else "", actor_text))
            # elif verb == " exiles ":
            #     text = "{}{}が追放。".format("お相手の" if is_opponent else "", target_text))
        if text:
            seikasey2.talk(text)

def on_error(ws, error):
    print("debug: called on_error")
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        print("debug: websocket is opened")

        while(True):
            line = sys.stdin.readline()
            if line != "":
                print("debug: sending value is " + line)
                ws.send(line)

    _thread.start_new_thread(run, ())


if __name__ == "__main__":

    param = sys.argv

    url = "ws://localhost:8089"

    if len(param) == 2:
        url = param[1]
        print("debug: param[1] is " + param[1])

    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(url,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()