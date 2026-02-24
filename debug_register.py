import asyncio
import json
from pyvts import vts

# --- 設定 ---
# 名前を少し変えて、重複エラーを回避してみます
TARGET_PARAMETER = "MyBrightnessV2" 
DEVELOPOER_NAME = "k-nishikawa21"
PLUGIN_NAME = "OBS Brightness Sync"

async def main():
    plugin_info = {
        "plugin_name": PLUGIN_NAME,
        "authentication_token_path": "token.txt"
    }
    myvts = vts(plugin_info=plugin_info)

    print("--- VTubeStudioに接続中 ---")
    try:
        await myvts.connect()
        await myvts.request_authenticate_token()
        await myvts.request_authenticate()
        print("接続成功！パラメータ作成を試みます...")

        # VTubeStudioからの「返事」をresponseという変数で受け取ります
        response = await myvts.request({
            "messageType": "ParameterCreationRequest",
            "data": {
                "parameterName": TARGET_PARAMETER,
                "developerName": DEVELOPOER_NAME,
                "explanation": "Created by Python",
                "min": 0,
                "max": 1,
                "defaultValue": 0
            }
        })

        # 【重要】返ってきた結果をそのまま表示します
        print("\n--- VTubeStudioからの返答 ---")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        print("------------------------------\n")

    except Exception as e:
        print(f"Pythonエラー発生: {e}")

    await myvts.close()

if __name__ == "__main__":
    asyncio.run(main())