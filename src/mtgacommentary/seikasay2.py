import re
import subprocess

class SeikaSay2:

    def __init__(self, seikasay2_path=".\\SeikaSay2.exe"):
        self.seikasay2_path = seikasay2_path

    def speak(self, cid, text, asynchronize=False, volume=None, speed=None, pitch=None, alpha=None, intonation=None, emotionEP=None, emotionP=None, overBanner=False):
        if cid and text:
            cmd = "{} -cid {}".format(self.seikasay2_path, cid)
            cmd += " -async" if asynchronize else ""
            cmd += " -volume {}".format(volume) if volume else ""
            cmd += " -speed {}".format(speed) if speed else ""
            cmd += " -pitch {}".format(pitch) if pitch else ""
            cmd += " -alpha {}".format(alpha) if alpha else ""
            cmd += " -intonation {}".format(intonation) if intonation else ""
            cmd += " -emotion {} {}".format(emotionEP, emotionP) if emotionEP and emotionP else ""
            cmd += " -ob" if overBanner else ""
            cmd += ' -t "{}"'.format(text)
            subprocess.run(cmd)
            return text
        else:
            return None
    
    def list(self):
        cids = []
        speakers = []
        cmd = "{} -list".format(self.seikasay2_path)
        try:
            s = subprocess.check_output(cmd)
            for line in s.splitlines():
                if type(line) is bytes:
                    line = line.decode("cp932")
                line = line.strip()
                print(line)
                if re.search(r"^[0-9]", line):
                    cids.append(int(line.split(" ")[0]))
                    speakers.append(line)
        except subprocess.CalledProcessError:
            return None
        return cids, speakers
        
