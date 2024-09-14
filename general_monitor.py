import sys
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
import os
import psutil
import shlex
import signal

def resolve_path(path):
    """Resolve relative paths to absolute paths."""
    if path.startswith(('python ', 'python3 ')):
        parts = shlex.split(path)
        parts[1] = os.path.abspath(parts[1])
        return ' '.join(parts)
    return os.path.abspath(path)

class MonitoredProgram:
    def __init__(self, program_path):
        self.original_path = program_path
        self.program_path = resolve_path(program_path)
        self.process = None
        self.status = "Stopped"
        self.terminal_process = None
        self.is_gui = True  # Assume GUI by default

    def start(self, options, run_in_terminal=False):
        if self.process is None or not psutil.pid_exists(self.process.pid):
            try:
                if self.program_path.startswith(("python ", "python3 ")):
                    parts = shlex.split(self.program_path)
                    command = [parts[0], parts[1]] + parts[2:] + options
                elif self.program_path.endswith('.py'):
                    command = [sys.executable, self.program_path] + options
                elif os.path.isfile(self.program_path):
                    command = [self.program_path] + options
                else:
                    command = shlex.split(self.program_path) + options
                
                print(f"Executing command: {' '.join(command)}")  # Debug print
                
                if run_in_terminal:
                    self.is_gui = False
                    if sys.platform == "win32":
                        self.terminal_process = subprocess.Popen(f'start cmd /k "{" ".join(command)}"', shell=True)
                    else:  # Unix-like systems
                        self.terminal_process = subprocess.Popen(['xfce4-terminal'] + command)
                    self.process = self.terminal_process
                else:
                    self.process = subprocess.Popen(command)
                
                self.status = "Running"
            except Exception as e:
                print(f"Error starting {self.program_path}: {e}")
                messagebox.showerror("Error", f"Error starting {self.program_path}: {e}")
        else:
            print(f"{self.program_path} is already running.")

    def stop(self):
        if self.process and psutil.pid_exists(self.process.pid):
            try:
                parent = psutil.Process(self.process.pid)
                children = parent.children(recursive=True)
                for child in children:
                    child.send_signal(signal.SIGTERM)
                parent.send_signal(signal.SIGTERM)
                
                # Wait for a short time and force kill if still running
                _, alive = psutil.wait_procs([parent] + children, timeout=3)
                for p in alive:
                    p.kill()
                
                self.status = "Stopped"
                self.process = None
                self.terminal_process = None
            except psutil.NoSuchProcess:
                pass
        else:
            print(f"{self.program_path} is not running.")

    def check_status(self):
        if self.process and psutil.pid_exists(self.process.pid):
            self.status = "Running"
        else:
            self.status = "Stopped"
        return self.status

    def bring_to_front(self):
        if self.process and psutil.pid_exists(self.process.pid):
            if self.is_gui:
                if sys.platform == "win32":
                    import win32gui
                    import win32com.client
                    shell = win32com.client.Dispatch("WScript.Shell")
                    shell.AppActivate(self.process.pid)
                elif sys.platform == "darwin":
                    os.system(f"osascript -e 'tell application \"System Events\" to set frontmost of every process whose unix id is {self.process.pid} to true'")
                elif sys.platform.startswith("linux"):
                    os.system(f"wmctrl -ia $(wmctrl -lp | awk '{{if ($3 == {self.process.pid}) print $1}}')")
            else:
                # For terminal apps, we need to bring the terminal window to front
                if sys.platform == "win32":
                    import win32gui
                    import win32com.client
                    shell = win32com.client.Dispatch("WScript.Shell")
                    shell.AppActivate(self.terminal_process.pid)
                elif sys.platform == "darwin":
                    os.system(f"osascript -e 'tell application \"Terminal\" to activate'")
                elif sys.platform.startswith("linux"):
                    os.system(f"wmctrl -ia $(wmctrl -lp | awk '{{if ($3 == {self.terminal_process.pid}) print $1}}')")
        else:
            print(f"{self.program_path} is not running.")

class UniversalMonitor:
    def __init__(self, master, programs):
        self.master = master
        self.master.title("Uni Mainz SHiPCalo general monitor")
        self.programs = {prog: MonitoredProgram(prog) for prog in programs}
        self.frames = {}
        
        for prog in self.programs:
            frame = ttk.Frame(master, padding="10 10 10 10")
            frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            label = ttk.Label(frame, text=os.path.basename(prog.split()[-1]), font=("Arial", 14, "bold"))
            label.pack(pady=5)
            
            status_label = ttk.Label(frame, text="Status: Stopped", font=("Arial", 12))
            status_label.pack(pady=5)
            
            start_button = ttk.Button(frame, text="Start", command=lambda p=prog: self.start_program(p))
            start_button.pack(side=tk.LEFT, padx=5)
            
            stop_button = ttk.Button(frame, text="Stop", command=lambda p=prog: self.stop_program(p))
            stop_button.pack(side=tk.RIGHT, padx=5)
            
            frame.bind("<Button-1>", lambda event, p=prog: self.bring_to_front(p))
            
            self.frames[prog] = frame

        self.master.after(1000, self.update_all_statuses)

    def start_program(self, prog):
        options, run_in_terminal = self.get_options()
        if options is not None:  # None means the user cancelled
            self.programs[prog].start(options, run_in_terminal)
            self.update_status(prog)

    def stop_program(self, prog):
        self.programs[prog].stop()
        self.update_status(prog)

    def bring_to_front(self, prog):
        self.programs[prog].bring_to_front()

    def update_status(self, prog):
        status = self.programs[prog].check_status()
        frame = self.frames[prog]
        status_label = frame.winfo_children()[1]
        status_label.config(text=f"Status: {status}")
        
        if status == "Running":
            frame.config(style="Running.TFrame")
        else:
            frame.config(style="Stopped.TFrame")

    def update_all_statuses(self):
        for prog in self.programs:
            self.update_status(prog)
        self.master.after(1000, self.update_all_statuses)

    def get_options(self):
        option_type = simpledialog.askstring("Option Type", "Enter 'file' to select a file, 'text' to enter options manually, or 'bash' to run in terminal:")
        if option_type == 'file':
            file_path = filedialog.askopenfilename(title="Select Option File")
            if file_path:
                return [file_path], False
            else:
                run_without_options = messagebox.askyesno("No File Selected", "Do you want to run without any options?")
                return ([], False) if run_without_options else (None, False)
        elif option_type == 'text':
            options = simpledialog.askstring("Enter Options", "Enter the options separated by space:")
            return (shlex.split(options) if options else [], False)
        elif option_type == 'bash':
            options = simpledialog.askstring("Enter Options", "Enter the options separated by space (or leave empty):")
            return (shlex.split(options) if options else [], True)
        else:
            return None, False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python general_monitor.py <program1> <program2> ...")
        sys.exit(1)

    root = tk.Tk()
    root.minsize(600,400) 
    style = ttk.Style()
    style.configure("Running.TFrame", background="green")
    style.configure("Stopped.TFrame", background="red")
    
    app = UniversalMonitor(root, sys.argv[1:])
    root.mainloop()
