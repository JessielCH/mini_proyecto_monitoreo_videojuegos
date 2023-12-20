from scr.monitor_controller import ProgramMonitor
def main():
    monitor = ProgramMonitor()

    try:
        while True:
            monitor.monitor_programs()
    except KeyboardInterrupt:
        print("Monitoring stopped.")

if __name__ == "__main__":
    main()