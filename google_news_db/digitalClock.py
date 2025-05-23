import time
import sys
from datetime import datetime

def live_datetime_display():
    try:
        while True:
            now = datetime.now()
            # Format: YYYY MM DD HH:MM:SS
            current_datetime = now.strftime("%Y %m %d %H:%M:%S")
            # Print and return to start of line
            print(f"\r{current_datetime}", end="", flush=True)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDisplay stopped")

if __name__ == "__main__":
    live_datetime_display()
