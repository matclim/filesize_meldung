import sys
import subprocess
import tkinter as tk
from tkinter import ttk, simpledialog

class MonitoredScript:
    def __init__(self, script_name):
        self.script_name = script_name
        self.process = None
        self.status = "Stopped"

    def start(self, options):
        if self.process is None or self.process.poll() is not None:
            command = [sys.executable, self.script_name] + options.split()
            self.process = subprocess.Popen(command)
            self.status = "Running"
        else:
            print(f"{self.script_name} is already running.")

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process.wait()
        self.status = "Stopped"

    def check_status(self):
        if self.process:
            if self.process.poll() is not None:
                self.status = "Stopped"
            else:
                self.status = "Running"
        return self.status

class GeneralMonitor:
    def __init__(self, master, scripts):
        self.master = master
        self.master.title("General Monitor")
        self.scripts = {script: MonitoredScript(script) for script in scripts}
        self.frames = {}
        
        for script in self.scripts:
            frame = ttk.Frame(master, padding="10 10 10 10")
            frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            label = ttk.Label(frame, text=script, font=("Arial", 14, "bold"))
            label.pack(pady=5)
            
            status_label = ttk.Label(frame, text="Status: Stopped", font=("Arial", 12))
            status_label.pack(pady=5)
            
            start_button = ttk.Button(frame, text="Start", command=lambda s=script: self.start_script(s))
            start_button.pack(side=tk.LEFT, padx=5)
            
            stop_button = ttk.Button(frame, text="Stop", command=lambda s=script: self.stop_script(s))
            stop_button.pack(side=tk.RIGHT, padx=5)
            
            self.frames[script] = frame

        self.master.after(1000, self.update_all_statuses)

    def start_script(self, script):
        options = simpledialog.askstring("Input", f"Enter options for {script}:")
        if options is not None:
            self.scripts[script].start(options)
            self.update_status(script)

    def stop_script(self, script):
        self.scripts[script].stop()
        self.update_status(script)

    def update_status(self, script):
        status = self.scripts[script].check_status()
        frame = self.frames[script]
        status_label = frame.winfo_children()[1]
        status_label.config(text=f"Status: {status}")
        
        if status == "Running":
            frame.config(style="Running.TFrame")
        else:
            frame.config(style="Stopped.TFrame")

    def update_all_statuses(self):
        for script in self.scripts:
            self.update_status(script)
        self.master.after(1000, self.update_all_statuses)

if __name__ == "__main__":
    if len(sys.argv) == 0:
        print("Usage: python general_monitor.py <script1.py> <script2.py> ...")
        sys.exit(1)

    root = tk.Tk()
    
    style = ttk.Style()
    style.configure("Running.TFrame", background="blue")
    style.configure("Stopped.TFrame", background="red")
    
    app = GeneralMonitor(root, sys.argv[1:])
    root.mainloop()
