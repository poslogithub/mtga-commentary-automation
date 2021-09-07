import _thread
import json
import re
import sys
import time
import websocket
from seikasay2 import SeikaSay2

seikasey2 = SeikaSay2()
hero_screen_name = ""
opponent_screen_name = ""

def on_message(ws, message):
    global hero_screen_name
    global opponent_screen_name

    text = ""
    blob = json.loads(message)
    print(blob)
    if blob and "game_history_event" in blob :
        text_array = blob.get("game_history_event")

        if len(text_array) == 1:
            if text_array[0].get("type") == "game":
                text = "対戦ありがとうございました。"
            elif text_array[0].get("type") == "turn":
                if text_array[0].get("text").find(opponent_screen_name) >= 0:
                    is_opponent = True
                text = "{}のターン。".format("お相手" if is_opponent else "こちら")
            else:
                print("debug: 不明なtype")
        else:
            verb = text_array[1].strip()
            if verb == "attacking":
                is_opponent = True if text_array[0].get("type") == "opponent" else False
                attacker = re.sub("（.+?）", "", text_array[0].get("text"))
                text = "{}{}でアタック。".format("お相手は" if is_opponent else "", attacker)
            elif verb == "blocks":
                is_opponent = True if text_array[0].get("type") == "opponent" else False
                blocker = re.sub("（.+?）", "", text_array[0].get("text"))
                attacker = re.sub("（.+?）", "", text_array[2].get("text"))
                text = "{}{}で{}をブロック。".format("お相手は" if is_opponent else "", blocker, attacker)
            elif verb == "casts":
                is_opponent = True if text_array[0].get("type") == "opponent" else False
                card = re.sub("（.+?）", "", text_array[2].get("text"))
                text = "{}{}をキャスト。".format("お相手は" if is_opponent else "", card)
            elif verb == "draws":
                if len(text_array) >= 3:
                    is_opponent = True if text_array[0].get("type") == "opponent" else False
                    card = re.sub("（.+?）", "", text_array[2].get("text"))
                    text = "{}{}をドロー。".format("お相手は" if is_opponent else "", card)
                else:
                    pass    # ドロー内容が不明の場合（＝対戦相手のドロー）は実況しない
            elif verb == "exiles":
                is_opponent = True if text_array[2].get("type") == "opponent" else False
                card = re.sub("（.+?）", "", text_array[2].get("text"))
                text = "{}{}を追放。".format("お相手の" if is_opponent else "", card)
            elif verb == "plays":
                is_opponent = True if text_array[0].get("type") == "opponent" else False
                card = re.sub("（.+?）", "", text_array[2].get("text"))
                text = "{}{}をプレイ。".format("お相手は" if is_opponent else "", card)
            elif verb == "resolves":
                pass    # 呪文の解決は実況しない
            elif verb == "sent to graveyard":
                is_opponent = True if text_array[0].get("type") == "opponent" else False
                card = re.sub("（.+?）", "", text_array[0].get("text"))
                reason = text_array[2]
                if reason in ["(Destroy)", "(SBA_Damage)", "(SBA_ZeroToughness)"]:
                    text = "{}{}が死亡。".format("お相手の" if is_opponent else "", card)
                elif reason == "(Conjure)":
                    text = "{}墓地に{}創出。".format("お相手の" if is_opponent else "", "が" if is_opponent else "を", card)
                elif reason == "(Discard)":
                    text = "{}{}{}をディスカード。".format("お相手は" if is_opponent else "", card)
                elif reason == "(Sacrifice)":
                    text = "{}{}{}生け贄に。".format("お相手の" if is_opponent else "", card, "が" if is_opponent else "を", card)
                elif reason == "(SBA_UnattachedAura)":
                    text = "{}{}が墓地に。".format("お相手の" if is_opponent else "", card)
                elif reason == "(nil)":
                    pass    # 不明な理由で墓地に落ちた場合（立ち消え等）は実況しない
                else:
                    print("debug: 不明なreason")
            elif verb == "vs":
                hero_screen_name = text_array[0].get("text")
                opponent_screen_name = text_array[2].get("text")
                text = "おっすおねがいしまーす。"
            elif verb == "'s":
                if len(text_array) >= 7 and text_array[5].strip() == "draws":
                    is_opponent = True if text_array[6].get("type") == "opponent" else False
                    card = re.sub("（.+?）", "", text_array[6].get("text"))
                    text = "{}をドロー。".format(card)
                if len(text_array) >= 7 and text_array[5].strip() == "exiles":
                    is_opponent = True if text_array[6].get("type") == "opponent" else False
                    card = re.sub("（.+?）", "", text_array[6].get("text"))
                    text = "{}をドロー。".format(card)
            elif verb == "'s life total changed":
                is_opponent = True if text_array[0].get("type") == "opponent" else False
                life_from = int(text_array[2].split(" -> ")[0])
                life_to = int(text_array[2].split(" -> ")[1])
                if not is_opponent and life_from > life_to:
                    text = "{}点くらって、ライフは{}。".format(life_from - life_to, life_to)
                elif not is_opponent and life_from < life_to:
                    text = "{}点回復して、ライフは{}。".format(life_to - life_from, life_to)
                elif not is_opponent and life_from > life_to:
                    text = "{}点あたえて、お相手のライフは{}。".format(life_from - life_to, life_to)
                elif not is_opponent and life_from < life_to:
                    text = "{}点回復されて、お相手のライフは{}。".format(life_to - life_from, life_to)
            elif verb == "'s starting hand:":
                text = "マリガンチェック。"
            else:
                print("debug: 不明なverb")

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