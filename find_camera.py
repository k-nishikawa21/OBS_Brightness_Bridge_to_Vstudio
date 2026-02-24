
from pygrabber.dshow_graph import FilterGraph

def show_cameras():
    graph = FilterGraph()
    devices = graph.get_input_devices()

    print("\n=== PCに接続されているカメラ一覧 ===")
    if not devices:
        print("カメラが見つかりませんでした。")
        return

    for index, name in enumerate(devices):
        print(f"番号: {index}  ->  名前: {name}")
    print("==================================\n")

    print("上記の番号をメモして、pupil_open.pyの設定で使用してください。")
    print("==================================\n")
    input("任意のキーを押して終了します...")
    


if __name__ == "__main__":
    show_cameras()