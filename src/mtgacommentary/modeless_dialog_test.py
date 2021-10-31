import tkinter as tk

class Application(tk.Frame):
    def __init__(self, master = None):
        super().__init__(master)

        self.master.title("Main")       # ウィンドウタイトル
        self.master.geometry("300x200") # ウィンドウサイズ(幅x高さ)

        # ボタンの作成
        btn_modeless = tk.Button(
            self.master, 
            text = "Modeless dialog",   # ボタンの表示名
            command = self.create_modeless_dialog    # クリックされたときに呼ばれるメソッド
            )
        btn_modeless.pack()

        btn_modal = tk.Button(
            self.master, 
            text = "Modal dialog",      # ボタンの表示名
            command = self.create_modal_dialog    # クリックされたときに呼ばれるメソッド
            )
        btn_modal.pack()

    def create_modeless_dialog(self):
        '''モードレスダイアログボックスの作成'''
        self.dlg_modeless = tk.Toplevel(self)
        self.dlg_modeless.title("Modeless Dialog")   # ウィンドウタイトル
        self.dlg_modeless.geometry("300x200")        # ウィンドウサイズ(幅x高さ)

    def create_modal_dialog(self):
        '''モーダルダイアログボックスの作成'''
        self.dlg_modal = tk.Toplevel(self)
        self.dlg_modal.title("Modal Dialog") # ウィンドウタイトル
        self.dlg_modal.geometry("300x200")   # ウィンドウサイズ(幅x高さ)

        # モーダルにする設定
        self.dlg_modal.grab_set()        # モーダルにする
        self.dlg_modal.focus_set()       # フォーカスを新しいウィンドウをへ移す
        self.dlg_modal.transient(self.master)   # タスクバーに表示しない

        btn_modal1 = tk.Button(
            self.dlg_modal, 
            text = "Close dialog",      # ボタンの表示名
            command = self.close_modal_dialog    # クリックされたときに呼ばれるメソッド
            )
        btn_modal1.pack()

        # ダイアログが閉じられるまで待つ
        app.wait_window(self.dlg_modal)  
        print("ダイアログが閉じられた")

    def close_modal_dialog(self):
        self.dlg_modal.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master = root)
    app.mainloop()