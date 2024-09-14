import subprocess
import time
import tkinter as tk
from tkinter import messagebox
import sys
import threading
import vlc
import os

class FileMonitor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.sound_path = "./alarmsound.mp3" 
        self.running = True
        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()
        media = self.vlc_instance.media_new(self.sound_path)
        self.player.set_media(media)

    def get_file_size(self):
        result = subprocess.run(['du', '-sh', self.file_path], capture_output=True, text=True)
        return result.stdout.strip()

    def play_sound(self):
        self.player.play()

    def show_warning(self):
        root = tk.Tk()
        root.withdraw()
        self.play_sound()
        if messagebox.showwarning("Warning", "File size hasn't changed in the last 2 minutes! Click OK to stop monitoring.", type=messagebox.OKCANCEL) == "ok":
            self.running = False
        self.player.stop()  # Stop the sound when the messagebox is closed

    def monitor_file_size(self):
        previous_size = None
        while self.running:
            current_size = self.get_file_size()
            print(f"Current size: {current_size}")
            
            if previous_size is not None and current_size == previous_size:
                self.show_warning()
                if not self.running:
                    break
            
            previous_size = current_size
            time.sleep(2)  # Wait for 2 minutes

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
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        sys.exit(1)
    
    print(f"Monitoring file: {file_path}")
    
    try:
        main(file_path)
    except Exception as e:
        print(f"An error occurred: {e}")
