import json
import os
import subprocess

class SeikaSay2:

    def __init__(self, config_file="config\\config.json"):
        with open(config_file, 'r', encoding="utf_8_sig") as rf:
            config =  json.load(rf)
        self.seikasay2_path = config.get("SeikaSay2Path", r".\\SeikaSay2.exe")
        if not os.path.isfile(self.seikasay2_path):
            self.seikasay2_path = r"SeikaSay2.exe"
        self.speak_alone = config.get("speakAlone", True)
        self.speak_opponent_only = config.get("speakOpponentOnly", False)
        self.hero_cid = config.get("heroCid", 0)
        self.opponent_cid = config.get("opponentCid", 0)
        # TODO: configでcid未指定時に話者一覧からcidを取得

        hero_file = "config\\{}.json".format(self.hero_cid)
        if not os.path.isfile(hero_file):
            hero_file = "config\\defaultSpeaker.json"
        with open(hero_file, 'r', encoding="utf_8_sig") as rf:
            self.hero = json.load(rf)

        opponent_file = "config\\{}.json".format(self.opponent_cid)
        if not os.path.isfile(opponent_file):
            opponent_file = "config\\defaultSpeaker.json"
        with open(opponent_file, 'r', encoding="utf_8_sig") as rf:
            self.opponent = json.load(rf)

    def speak(self, is_opponent=False, message_type="", verb="", attacker="", blocker="", card="", source="", reason="", life_from=0, life_to=0):
        life_diff = 0

        if not is_opponent and self.speak_opponent_only:    # speak_opponent_onlyならば、is_opponentの時だけ話す。
            return ""

        if self.speak_alone or not is_opponent: # speak_aloneの時はheroが話す。speak_aloneでない時はis_opponentでないならheroが話す。
            cid = self.hero_cid
            speaker = self.hero
            speak_idx = 0 if not is_opponent else 1 # 0: heroが自分のアクションを話す。1: heroが対戦相手のアクションを話す。
        else:
            cid = self.opponent_cid
            speaker = self.opponent
            speak_idx = 2 # 2: opponentが自分のアクションを話す。

        cmd = "{} -cid {} -async".format(self.seikasay2_path, cid)

        speak_obj = None
        if message_type in ["game", "turn"]:
            for obj in speaker:
                if obj.get("type") == message_type:
                    speak_obj = obj.get("speak")[speak_idx]
                    break
        elif verb in ["attacking", "blocks", "casts", "draws", "exiles", "plays", "resolves", "sent to graveyard", "vs", "'s life total changed", "'s starting hand:"]:
            for obj in speaker:
                if obj.get("verb") == verb:
                    if verb == "sent to graveyard":
                        if reason not in obj.get("reason"):
                            continue
                    if verb == "'s life total changed":
                        if obj.get("life") == "gain" and life_from - life_to > 0:
                            continue
                        if obj.get("life") == "lose" and life_from - life_to < 0:
                            continue
                        life_diff = abs(life_from - life_to)
                    speak_obj = obj.get("speak")[speak_idx]
                    break

        if speak_obj and speak_obj.get("text"):
            text = speak_obj.get("text").replace(r"{attacker}", attacker).replace(r"{blocker}", blocker).replace(r"{card}", card).replace(r"{source}", source).replace(r"{life_from}", str(life_from)).replace(r"{life_to}", str(life_to)).replace(r"{life_diff}", str(life_diff))
            cmd += " -t \"{}\"".format(text)
            cmd += " -volume {}".format(speak_obj.get("volume")) if speak_obj.get("volume") else ""
            cmd += " -speed {}".format(speak_obj.get("speed")) if speak_obj.get("speed") else ""
            cmd += " -pitch {}".format(speak_obj.get("pitch")) if speak_obj.get("pitch") else ""
            cmd += " -alpha {}".format(speak_obj.get("alpha")) if speak_obj.get("alpha") else ""
            cmd += " -intonation {}".format(speak_obj.get("intonation")) if speak_obj.get("intonation") else ""
            if speak_obj.get("emotionEP") and speak_obj.get("emotionP"):
                cmd += " -emotion {} {}".format(speak_obj.get("emotionEP"), speak_obj.get("emotionP"))
            cmd += " -ob" if speak_obj.get("overBanner") else ""
            subprocess.run(cmd)
            return text
        else:
            return ""
    
    def list(self):
        cmd = "{} -list".format(self.seikasay2_path)
        return subprocess.run(cmd)
