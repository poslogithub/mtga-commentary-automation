import json
import os
import re
import subprocess

class SeikaSay2:

    def __init__(self, config_file="config\\config.json"):
        with open(config_file, 'r', encoding="utf_8_sig") as rf:
            config =  json.load(rf)
        self.seikasay2_path = config.get("SeikaSay2Path", r".\\SeikaSay2.exe")
        if not os.path.isfile(self.seikasay2_path):
            self.seikasay2_path = r"SeikaSay2.exe"
        self.speak_duo = config.get("speakDuo", False)
        self.speak_opponent_only = config.get("speakOpponentOnly", False)
        self.hero_cid = config.get("heroCid", 0)
        self.opponent_cid = config.get("opponentCid", 0)
        # TODO: configでcid未指定時に話者一覧からcidを取得

    def speak(self, is_opponent=False, message_type="", verb="", attacker="", blocker="", card="", source="", reason="", life_from=0, life_to=0):
        life_diff = 0

        if not is_opponent and self.speak_opponent_only:    # speak_opponent_onlyならば、is_opponentの時だけ話す。
            return ""

        if not self.speak_duo or not is_opponent:  # speak_duoでないか、is_opponentでなければheroが話す。
            cid = self.hero_cid
            speaker = self.hero
            speak_idx = 0 if not is_opponent else 1 # 0: heroが自分のアクションを話す。1: heroが対戦相手のアクションを話す。
        else:   # speak_duoかつis_opponentならばopponentが話す。
            cid = self.opponent_cid
            speaker = self.opponent
            speak_idx = 2 # 2: opponentが自分のアクションを話す。

        cmd = "{} -cid {}".format(self.seikasay2_path, cid)

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
        
        speak_param_obj = None
        for obj in speaker:
            if obj.get("type") == "SeikaSay2":
                speak_param_obj = obj
                break
        if speak_param_obj and speak_obj:
            speak_param_obj["volume"] = speak_obj.get("volume") if speak_obj.get("volume") else speak_param_obj.get("volume")
            speak_param_obj["speed"] = speak_obj.get("speed") if speak_obj.get("speed") else speak_param_obj.get("speed")
            speak_param_obj["pitch"] = speak_obj.get("pitch") if speak_obj.get("pitch") else speak_param_obj.get("pitch")
            speak_param_obj["alpha"] = speak_obj.get("alpha") if speak_obj.get("alpha") else speak_param_obj.get("alpha")
            speak_param_obj["intonation"] = speak_obj.get("intonation") if speak_obj.get("intonation") else speak_param_obj.get("intonation")
            speak_param_obj["emotionEP"] = speak_obj.get("emotionEP") if speak_obj.get("emotionEP") else speak_param_obj.get("emotionEP")
            speak_param_obj["emotionP"] = speak_obj.get("emotionP") if speak_obj.get("emotionP") else speak_param_obj.get("emotionP")
            speak_param_obj["overBanner"] = speak_obj.get("overBanner") if speak_obj.get("overBanner") else speak_param_obj.get("overBanner")

        if speak_obj and speak_obj.get("text"):
            cmd += " -volume {}".format(speak_param_obj.get("volume")) if speak_param_obj.get("volume") else ""
            cmd += " -speed {}".format(speak_param_obj.get("speed")) if speak_param_obj.get("speed") else ""
            cmd += " -pitch {}".format(speak_param_obj.get("pitch")) if speak_param_obj.get("pitch") else ""
            cmd += " -alpha {}".format(speak_param_obj.get("alpha")) if speak_param_obj.get("alpha") else ""
            cmd += " -intonation {}".format(speak_param_obj.get("intonation")) if speak_param_obj.get("intonation") else ""
            if speak_param_obj.get("emotionEP") and speak_param_obj.get("emotionP"):
                cmd += " -emotion {} {}".format(speak_param_obj.get("emotionEP"), speak_param_obj.get("emotionP"))
            cmd += " -ob" if speak_param_obj.get("overBanner") else ""
            text = speak_obj.get("text").replace(r"{attacker}", attacker).replace(r"{blocker}", blocker).replace(r"{card}", card).replace(r"{source}", source).replace(r"{life_from}", str(life_from)).replace(r"{life_to}", str(life_to)).replace(r"{life_diff}", str(life_diff))
            cmd += " -t \"{}\"".format(text)
            subprocess.run(cmd)
            return text
        else:
            return ""
    
    def cid_list(self):
        rst = []
        cmd = "{} -list".format(self.seikasay2_path)
        try:
            s = subprocess.check_output(cmd)
            for line in s.splitlines():
                if type(line) is bytes:
                    line = line.decode("cp932")
                line = line.strip()
                print(line)
                if re.search("^[0-9]", line):
                    rst.append(line.split(" ")[0])
        except subprocess.CalledProcessError:
            return None
        return rst

    def set_cids(self, hero_cid, opponent_cid):
        if self.hero_cid == 0:
            self.hero_cid = hero_cid
        hero_file = "config\\{}.json".format(self.hero_cid)
        if not os.path.isfile(hero_file):
            hero_file = "config\\defaultSpeaker.json"
        with open(hero_file, 'r', encoding="utf_8_sig") as rf:
            self.hero = json.load(rf)

        if self.opponent_cid == 0:
            self.opponent_cid = opponent_cid
        opponent_file = "config\\{}.json".format(self.opponent_cid)
        if not os.path.isfile(opponent_file):
            opponent_file = "config\\defaultSpeaker.json"
        with open(opponent_file, 'r', encoding="utf_8_sig") as rf:
            self.opponent = json.load(rf)


    def get_speaker_cid(self, is_opponent):
        cid, _, _ = self.get_speaker(is_opponent)
        print(cid)
        return cid

    def speak_config(self):
        if not self.speak_duo and not self.speak_opponent_only:
            subprocess.run("{} -cid {} -t {}".format(self.seikasay2_path, self.hero_cid, "自分と対戦相手のアクションを実況します。"))
        elif not self.speak_duo and self.speak_opponent_only:
            subprocess.run("{} -cid {} -t {}".format(self.seikasay2_path, self.hero_cid, "対戦相手のアクションだけを実況します。"))
        elif self.speak_duo and not self.speak_opponent_only:
            subprocess.run("{} -cid {} -t {}".format(self.seikasay2_path, self.hero_cid, "自分のアクションを実況します。"))
            subprocess.run("{} -cid {} -t {}".format(self.seikasay2_path, self.opponent_cid, "対戦相手のアクションを実況します。"))
        elif self.speak_duo and self.speak_opponent_only:
            subprocess.run("{} -cid {} -t {}".format(self.seikasay2_path, self.opponent_cid, "対戦相手のアクションだけを実況します。"))
