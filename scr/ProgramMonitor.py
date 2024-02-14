import os
import psutil
import time
import datetime
from pymongo import MongoClient
from geopy.distance import geodesic
import smtplib
from email.mime.text import MIMEText
import requests

class LocationMonitor:
    def __init__(self):
        self.target_location = None

    def get_current_location(self):
        try:
            ip_info = requests.get("https://ipinfo.io").json()
            location_str = ip_info.get("loc", "")

            if location_str:
                latitude, longitude = map(float, location_str.split(","))
                return latitude, longitude
            else:
                print("No se pudo obtener la ubicación actual.")
                return None
        except Exception as e:
            print(f"Error obteniendo la ubicación actual: {e}")
            return None

    def is_outside_target_area(self):
        current_location = self.get_current_location()
        if current_location:
            distance = geodesic(current_location, self.target_location).meters
            return distance > 100
        else:
            return False

class EmailNotifier:
    def __init__(self, sender_email, sender_password, receiver_email):
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.receiver_email = receiver_email

    def send_email(self, subject, message):
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(self.sender_email, self.sender_password)

            msg = MIMEText(message)
            msg["Subject"] = subject
            msg["From"] = self.sender_email
            msg["To"] = self.receiver_email

            server.sendmail(self.sender_email, self.receiver_email, msg.as_string())
            server.quit()
        except Exception as e:
            print(f"Error sending email: {e}")

class ProgramMonitor:
    def __init__(self):
        self.PROGRAMS_TO_LOG = []
        self.PREVIOUS_STATE = set()
        self.LOG_FILE_PATH = os.path.abspath("program_log.txt")
        self.location_monitor = LocationMonitor()
        self.is_monitoring_enabled = True
        
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["program_monitor"]
        self.collection = self.db["program_logs"]

        self.email_notifier = EmailNotifier(sender_email="BryanDaviid333@gmail.com",
                                           sender_password="ffco lbue izbz ryeh",
                                           receiver_email="davidchalan54@gmail.com")

    def enable_monitoring(self):
        self.is_monitoring_enabled = True

    def disable_monitoring(self):
        self.is_monitoring_enabled = False

    def filter_inappropriate_programs(self, program_name):
        return program_name.lower() in [p.lower() for p in self.PROGRAMS_TO_LOG]

    def check_and_take_action(self):
        if self.is_monitoring_enabled and self.location_monitor.is_outside_target_area():
            subject = "¡Alerta! Saliste del área designada"
            message = "Se detectó que has salido del área designada. Por favor, verifica tu ubicación."
            self.email_notifier.send_email(subject, message)

    def log_program_execution(self, program_name, username, action, cpu_percent, memory_percent):
        log_entry = {
            "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "program_name": program_name,
            "username": username,
            "action": action,
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent
        }

        try:
            self.collection.insert_one(log_entry)
        except Exception as e:
            print(f"Error writing to MongoDB: {e}")

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
                    self.log_program_execution(program_name, username, "running