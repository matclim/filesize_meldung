import subprocess
import time
import tkinter as tk
from tkinter import messagebox
import sys
import threading

class FileMonitor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.running = True

    def get_file_size(self):
        result = subprocess.run(['du', '-sh', self.file_path], capture_output=True, text=True)
        return result.stdout.strip()

    def show_warning(self):
        root = tk.Tk()
        root.withdraw()
        if messagebox.showwarning("Warning", "Issue with the File!", type=messagebox.OKCANCEL) == "ok":
            self.running = False

    def monitor_file_size(self):
        previous_size = None
        while self.running:
            current_size = self.get_file_size()
            print(f"Current size: {current_size}")
            
            if current_size == previous_size:
                self.show_warning()
                if not self.running:
                    break
            
            previous_size = current_size
            time.sleep(1)  # Wait for 2 minutes

        print("Monitoring stopped.")

def main(file_path):
    monitor = FileMonitor(file_path)
    monitor_thread = threading.Thread(target=monitor.monitor_file_size)
    monitor_thread.start()
    monitor_thread.join()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    print(f"Monitoring file: {file_path}")
    main(file_path)
