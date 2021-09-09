import subprocess
import json

class SeikaSay2:

    def __init__(self, config_file="config\\config.json")
    with json.load(config_file) as config:
        self.seikasay2_path = config.("SeikaSay2Path")
        if self.seikasay2_path == None:
            if os.path.isfile(r".\\SeikaSay2.exe"):
                seikasay2_path = r".\\SeikaSay2.exe"
            else:
                self.seikasay2_path = r"SeikaSay2.exe"
        
        # speakAloneを取得
        
        self.hero_cid = config.get("heroCid")
        if self.hero_cid == None:
            self.hero_cid = 1707    # TODO: 話者一覧から取得

        self.opponent_cid = config.get("heroOpponentCid")
        if self.opponent_cid == None:
            self.opponent_cid = 1707    # TODO: 話者一覧から取得
    
    # TODO: heroとopponentのjsonファイルをロード
    # TODO: SeikaSay2にverbとis_opponentとその他諸々渡して、SeikaSay2側で話す内容を決めたほうが良いのでは？

    def speak(self, text="", hero_cid=0):
        cmd = "{} -cid {} -async -t {}".format(self.seikasay2_path, hero_cid if hero_cid > 0 else self.hero_cid, text)
        subprocess.run(cmd)
    
    def list(self):
        cmd = "{} --list"
