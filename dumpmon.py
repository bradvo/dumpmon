# dumpmon.py
# Author: Jordan Wright
# Version: 0.0 (in dev)

# ---------------------------------------------------
# To Do:
#
#	- Refine Regex
#	- Create/Keep track of statistics

from lib.regexes import regexes
from lib.Pastebin import Pastebin, PastebinPaste
from lib.Slexy import Slexy, SlexyPaste
from lib.Pastie import Pastie, PastiePaste
from lib.helper import log
from time import sleep
from settings import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, log_file
import threading
import logging
import sys


def monitor():
    '''
    monitor() - Main function... creates and starts threads

    '''
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--verbose", help="more verbose", action="store_true")
    args = parser.parse_args()  
    level = logging.INFO
    if args.verbose:
        level = logging.DEBUG
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(message)s', datefmt="%d-%m-%Y %H:%M:%S", filename=log_file, level=level)
    logging.info('Monitoring...')
    ### To enable tweets, uncomment the following lines ###
    '''bot = Twitter(
        auth=OAuth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET,
            CONSUMER_KEY, CONSUMER_SECRET)
        )'''
    ### And delete the next ones ###
    bot = None
    ##########
    # Create lock for both output log and tweet action
    log_lock = threading.Lock()
    tweet_lock = threading.Lock()

    if not os.path.isdir("saves"):
        try:
            os.makedirs("saves")
        except Exception:
            logging.error("Failed to create the 'saves' directory")
            sys.exit()

    pastebin_thread = threading.Thread(
        target=Pastebin().monitor, args=[bot, tweet_lock])
    slexy_thread = threading.Thread(
        target=Slexy().monitor, args=[bot, tweet_lock])
    pastie_thead = threading.Thread(
        target=Pastie().monitor, args=[bot, tweet_lock])

    for thread in (pastebin_thread, slexy_thread, pastie_thead):
        thread.daemon = True
        thread.start()

    # Let threads run
    try:
        while(1):
            sleep(5)
    except KeyboardInterrupt:
        logging.warn('Stopped.')


if __name__ == "__main__":
    monitor()
