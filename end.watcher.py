from watchdog.observers.polling import PollingObserver
from watchdog.events import RegexMatchingEventHandler
import time
import requests
import yaml

# LINE にメッセージを送信する
def line_notify(msg, TOKEN):
    try:
        access_token = TOKEN
        msg = msg + "\nテストが完了しました。"
        
        headers = {'Authorization': 'Bearer ' + access_token}
        payload = {'message': msg}
        
        print("LINE メッセージを POST します。")
        r = requests.post(LINE_NOTIFY_URL, headers=headers, params=payload,)
        if r.status_code == 200:
            print("LINE メッセージを送信しました。")
        else:
            print("ステータスコード: " + r.status_code)
            raise Exception
    except Exception as e:
        print(e)

class MyFileWatchHandler(RegexMatchingEventHandler):
    def __init__(self, regexes):
        super().__init__(regexes=regexes)

    # ファイル作成時の動作
    def on_created(self, event):
        filepath = event.src_path
        line_notify(filepath, TOKEN)


if __name__ == "__main__":

    # config を読み込む
    try:
        with open("./config.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        # LINE_NOTIFY_URL
        LINE_NOTIFY_URL = config["chat_url"]
        # LINE access_token
        TOKEN = config["access_token"]
        # 監視対象パス
        TARGET_PATH = config["target_path"]
    except Exception as e:
        print(e)

    # 対象ファイルパスのパターン
    PATTERNS = [r'.+report-.+.html$']

    # 監視を開始する
    event_handler = MyFileWatchHandler(PATTERNS)
    observer = PollingObserver()
    observer.schedule(event_handler, TARGET_PATH, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    