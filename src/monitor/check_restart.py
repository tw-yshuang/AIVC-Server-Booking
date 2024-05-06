import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEvent, FileSystemEventHandler

PROJECT_DIR = Path(__file__).resolve().parents[2]
MONITOR_EXEC = PROJECT_DIR / 'jobs/monitor_exec'

if __name__ == '__main__':
    import sys

    sys.path.append(str(PROJECT_DIR))


def get_last_line(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        if lines:
            return lines[-1].strip()
        else:
            return None


class OnMyWatch:
    watchFile: Path = MONITOR_EXEC

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.watchFile, recursive=False)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Observer Stopped")

        self.observer.join()


class Handler(FileSystemEventHandler):
    def on_modified(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return None

        id = get_last_line(MONITOR_EXEC)
        exec_str = f'docker restart {id}'
        result = subprocess.run(exec_str.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8').stdout[:-1]
        # TODO: log the operation to the `monitor.log`
        return


if __name__ == '__main__':
    watch = OnMyWatch()
    watch.run()
