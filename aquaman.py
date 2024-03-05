import datetime
import sys
import threading
from src.recognizer.screen_scraper_mapping import ScreenScraper
from src.tools.screen_operations import ScreenshotUtil

version = "0.0.1"



class ThreadManager(threading.Thread):
    pass



class GameBotThread:
    def __init__(self, window_title, platform, max_player):
        self.window_title = window_title
        self.platform = platform
        self.max_player = max_player

        self.recognizer = None
        self.decision_maker = None
        self.printer = None
        self.action_performer = None
    
    def it_is_my_turn(self):
        pass

    def run(self):
        while True:
            windowshot = self.shoter.capture_screen()
            if self.it_is_my_turn():
                # scraper()
                # hands_converter()
                # decision_maker()
                # action_performer()
                pass
            else:
                pass



# ==== MAIN PROGRAM =====
def aquaman():
    print("Aquaman version: " + version)
    print("Aquaman is a poker bot that plays Texas Hold'em poker games.")
    print("It uses a combination of computer vision and machine learning to play the game.")
    print("Aquaman is a work in progress and is not yet ready for public use.")
    print("Thank you for your interest in Aquaman.")
    print("Goodbye!")

    # init_logger(screenlevel=logging.INFO, filename='deepmind_pokerbot', logdir='log')
    # # print(f"Screenloglevel: {screenloglevel}")
    # log = logging.getLogger("")
    # log.info("Initializing program")


    # Back up the reference to the exceptionhook

    def exception_hook(exctype, value, traceback):
        # Print the error and traceback
        # logger
        pass
        
        # Call the normal Exception hook after
    
    # Set the exception hook to our wrapping function

    t1 = ThreadManager() # ui_thread()
    # t1.start()
    t2 = ThreadManager() # bot_thread()
    # t2.start()

    try:
        # sys.exit(app.exec_())
        pass
    except:
        print("Exiting...")
        # monitor_signals.exit_thread = True

if __name__ == '__main__':
    aquaman()
