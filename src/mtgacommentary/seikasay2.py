import subprocess

class SeikaSay2:
    cid = 1707  # 東北きりたん EX
    seikasay2_path = "C:\\Program Files\\510product\\SeikaSay2\\SeikaSay2.exe"

    def talk(self, text="", cid=0):
        cmd = "{} -cid {} -async -t {}".format(self.seikasay2_path, cid if cid > 0 else self.cid, text)
        subprocess.run(cmd)
