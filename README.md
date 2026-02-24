# OBS Brightness Sync for VTube Studio

PCの画面の明るさ（またはWebカメラの映像）をリアルタイムに取得し、VTube Studio (VTS) のアバターパラメータと連動させるためのPythonアプリケーションです．
OBSの仮想カメラ等と組み合わせることで、「ゲーム画面が明るいと瞳孔が縮む」「暗いシーンで目にハイライトが入る」といった、環境光に合わせた動的なアバター表現が可能になります．

## ✨ 特徴 (Features)
* **シンプルなGUI**: Tkinterによる軽量な操作画面で、直感的に設定が可能．
* **リアルタイム解析**: OpenCVを使用してカメラ映像の平均輝度を高速に計算．
* **反転オプション (Invert)**: 「明るい=0, 暗い=1」といった値の反転処理にチェックボックス一つで対応．
* **設定の自動保存**: 次回起動時も前回の設定 (`settings.json`) をそのまま引き継ぎます．

## 📦 動作環境 (Requirements)
* Python 3.8 以上推奨
* VTube Studio (設定からAPIを有効化しておく必要があります)

### 依存ライブラリ
以下のライブラリを使用しています．
* `opencv-python`
* `numpy`
* `pyvts`
* `pygrabber` (Windows環境でのカメラデバイス取得用)

インストールコマンド:
```bash
pip install opencv-python numpy pyvts pygrabber
```
