import bot
import threading

def run_bot():
    bot.startBot()

def run_updater():
    print("Running updater...")

thread = threading.Thread(target=run_updater, daemon=True)
thread.start()

def main():
    run_bot()

if __name__ == "__main__":
    main()