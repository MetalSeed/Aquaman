import datetime
import sys
import threading

version = "0.0.1"

class ThreadManager(threading.Thread):
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
