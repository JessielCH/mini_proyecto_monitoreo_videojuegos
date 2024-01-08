import os
import psutil
import time
import datetime

class ProgramMonitor:
    def __init__(self):
        self.PROGRAMS_TO_LOG = []
        self.PREVIOUS_STATE = set()
        self.LOG_FILE_PATH = os.path.abspath("program_log.txt")

    def filter_inappropriate_programs(self, program_name):
        return program_name.lower() in [p.lower() for p in self.PROGRAMS_TO_LOG]

    def log_program_execution(self, program_name, username, action, cpu_percent, memory_percent):
        try:
            with open(self.LOG_FILE_PATH, "a") as log_file:
                log_file.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {program_name} executed by {username}. Action: {action}. "
                               f"CPU: {cpu_percent:.2f}%, Memory: {memory_percent:.2f}%\n")
        except Exception as e:
            print(f"Error writing to log file: {e}")

    def monitor_programs(self):
        for process in psutil.process_iter(["name", "username", "cpu_percent", "memory_percent"]):
            program_name = process.info.get("name", "")
            username = process.info.get("username", "")
            cpu_percent = process.info.get("cpu_percent", 0.0)
            memory_percent = process.info.get("memory_percent", 0.0)

            if self.filter_inappropriate_programs(program_name):
                if program_name.lower() not in self.PREVIOUS_STATE:
                    self.log_program_execution(program_name, username, "started", cpu_percent, memory_percent)
                    self.PREVIOUS_STATE.add(program_name.lower())
                else:
                    self.log_program_execution(program_name, username, "running", cpu_percent, memory_percent)

        time.sleep(10)

    def start_monitoring(self):
        os.makedirs(os.path.dirname(self.LOG_FILE_PATH), exist_ok=True)

        if not os.path.exists(self.LOG_FILE_PATH):
            with open(self.LOG_FILE_PATH, "w"):
                pass

        try:
            while True:
                self.monitor_programs()
        except KeyboardInterrupt:
            print("Monitoring stopped.")
