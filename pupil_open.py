import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
import threading
import asyncio
import json
import os
from pyvts import vts

# --- 定数 ---
PLUGIN_NAME = "OBS Brightness Sync"
DEVELOPER_NAME = "k-nishikawa21"
SETTINGS_FILE = "settings.json"

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("VTS 瞳孔シンクロ (Simple)")
        self.root.geometry("350x380")
        self.root.attributes("-topmost", True)

        self.is_running = False
        self.thread = None

        # デフォルト設定
        self.settings = {
            "target_param": "MyBrightness",
            "camera_index": 0,
            "interval": 0.1,
            # "show_log": True,
            "invert": False
        }
        self.load_settings()

        # --- GUI構築 ---
        self.create_widgets()

    def create_widgets(self):
        # 1. 設定エリア
        frame_settings = ttk.LabelFrame(self.root, text="設定")
        frame_settings.pack(padx=10, pady=10, fill="x")

        # パラメータ名
        ttk.Label(frame_settings, text="送信先パラメータ:").pack(anchor="w", padx=10, pady=(5, 0))
        self.var_param = tk.StringVar(value=self.settings["target_param"])
        ttk.Entry(frame_settings, textvariable=self.var_param).pack(fill="x", padx=10, pady=5)

        # カメラ番号
        ttk.Label(frame_settings, text="カメラ番号:").pack(anchor="w", padx=10)
        self.var_camera = tk.IntVar(value=self.settings["camera_index"])
        ttk.Entry(frame_settings, textvariable=self.var_camera).pack(fill="x", padx=10, pady=5)

        # 通信間隔
        ttk.Label(frame_settings, text="通信間隔(秒):").pack(anchor="w", padx=10)
        self.var_interval = tk.DoubleVar(value=self.settings["interval"])
        ttk.Spinbox(frame_settings, from_=0.01, to=2.0, increment=0.05, textvariable=self.var_interval).pack(fill="x", padx=10, pady=5)

        # 2. オプションエリア
        frame_opt = ttk.LabelFrame(self.root, text="オプション")
        frame_opt.pack(padx=10, pady=5, fill="x")

        # 反転スイッチ (Invert)
        self.var_invert = tk.BooleanVar(value=self.settings["invert"])
        ttk.Checkbutton(frame_opt, text="値を反転する (明るい = 0)", variable=self.var_invert).pack(anchor="w", padx=10, pady=5)

        # ログ表示スイッチ
        # self.var_log = tk.BooleanVar(value=self.settings["show_log"])
        # ttk.Checkbutton(frame_opt, text="ターミナルにログを表示", variable=self.var_log).pack(anchor="w", padx=10, pady=5)

        # 3. 実行エリア
        self.status_label = ttk.Label(self.root, text="停止中", foreground="gray")
        self.status_label.pack(pady=(10, 0))
        
        # 簡易インジケーター（数字のみ）
        self.val_label = ttk.Label(self.root, text="Value: ---", font=("Meiryo", 10, "bold"))
        self.val_label.pack(pady=0)

        self.btn_start = ttk.Button(self.root, text="設定を保存して開始", command=self.toggle_sync)
        self.btn_start.pack(pady=10, ipady=5, fill="x", padx=20)

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                    self.settings.update(data)
            except:
                pass

    def save_settings(self):
        self.settings["target_param"] = self.var_param.get()
        self.settings["camera_index"] = self.var_camera.get()
        self.settings["interval"] = self.var_interval.get()
        # self.settings["show_log"] = self.var_log.get()
        self.settings["invert"] = self.var_invert.get()

        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings, f, indent=4)

    def toggle_sync(self):
        if not self.is_running:
            self.save_settings() # 開始時に保存
            self.is_running = True
            self.btn_start.config(text="停止")
            self.status_label.config(text="同期中...", foreground="green")
            self.thread = threading.Thread(target=self.run_logic_wrapper, daemon=True)
            self.thread.start()
        else:
            self.is_running = False
            self.btn_start.config(text="設定を保存して開始")
            self.status_label.config(text="停止中", foreground="red")

    def run_logic_wrapper(self):
        asyncio.run(self.main_logic())

    async def main_logic(self):
        plugin_info = {
            "plugin_name": PLUGIN_NAME,
            "developer": DEVELOPER_NAME,
            "authentication_token_path": "token.txt"
        }
        myvts = vts(plugin_info=plugin_info)
        
        try:
            await myvts.connect()
            await myvts.request_authenticate_token()
            await myvts.request_authenticate()
            
            # パラメータ登録（毎回実行して確実性を担保）
            target = self.var_param.get()
            await myvts.request({
                "apiName": "VTubeStudioPublicAPI",
                "apiVersion": "1.0",
                "requestID": "CreateParam",
                "messageType": "ParameterCreationRequest",
                "data": {
                    "parameterName": target,
                    "explanation": "Created by Python Script",
                    "min": 0, "max": 1, "defaultValue": 0
                }
            })
        except Exception as e:
            print(f"接続エラー: {e}")
            self.is_running = False
            self.status_label.config(text="接続エラー")
            return

        cap = cv2.VideoCapture(self.var_camera.get(), cv2.CAP_DSHOW)
        
        while self.is_running:
            ret, frame = cap.read()
            if not ret:
                await asyncio.sleep(1)
                continue

            # 処理
            small = cv2.resize(frame, (320, 180))
            gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
            val = min(max(np.mean(gray) / 255.0, 0.0), 1.0)

            # 反転処理
            if self.var_invert.get():
                val = 1.0 - val

            # GUI表示更新
            self.val_label.config(text=f"Value: {val:.2f}")

            """
            # ログ表示
            if self.var_log.get():
                print(f"明るさ: {val:.2f} -> {target}")
            """
                
            # 送信
            try:
                await myvts.request({
                    "apiName": "VTubeStudioPublicAPI",
                    "apiVersion": "1.0",
                    "requestID": "InjectParam",
                    "messageType": "InjectParameterDataRequest",
                    "data": {
                        "mode": "set",
                        "parameterValues": [
                            { "id": target, "value": val }
                        ]
                    }
                })
            except:
                pass
            
            await asyncio.sleep(self.var_interval.get())
        
        cap.release()
        await myvts.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()