import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

PROJECT_DIR = Path(__file__).resolve().parents[2]
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
	watchDirectory: Path = PROJECT_DIR / 'jobs/monitor_exec'
    
	def __init__(self):
		self.observer = Observer()

	def run(self):
		event_handler = Handler()
		self.observer.schedule(event_handler, self.watchDirectory, recursive = True)
		self.observer.start()
		try:
			while True:
				time.sleep(5)
		except:
			self.observer.stop()
			print("Observer Stopped")

		self.observer.join()


class Handler(FileSystemEventHandler):
	
	@staticmethod
	def on_any_event(event):
		if event.is_directory:
			return None
		elif event.event_type == 'modified':
			id = get_last_line(PROJECT_DIR / 'jobs/monitor_exec')
			exec_str = f"docker restart {id.lower()}"
			result = subprocess.run(
                    exec_str.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8'
                ).stdout[:-1]
			print(result)

if __name__ == '__main__':
	watch = OnMyWatch()
	watch.run()
