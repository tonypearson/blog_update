#!/usr/bin/python3
# Tony Pearson, IBM, July 2020
""" getframes.py
    This program launches browser against one or more topic blogs
    in the IBM Storage Community.  For each frame containing up
    to 20 posts, it saves the frame, then proceeds to the next
    frame.  All of the frames can be captured in this manner.

    Usage:
    $ getframes.py <group>
    where group is one of 'flash','mdp', etc.

    $ getframes.py
    (without parameters will delete all previous frames, and
     fetch all the frames from all topic groups)
"""

# imports
import os
import re
import sys
import logging
import datetime
from selenium import webdriver
from logSystem import logSystem
from pageClass import HomePage, FramePage, COMKEYS, FRAMESDIR
from functions import get_modname, setup_logging

TOPICS = list(COMKEYS.keys())

def get_parms(argv):

    # Allow individual topic, '*', or nothing (which defaults to *)
    if len(argv) > 1:
        comkey = argv[1]
        if comkey != '*' and comkey not in COMKEYS:
            print('   Error, invalid topic group "' + comkey + '"')
            print('   Parameter must be one of: ', ', '.join(TOPICS))
            print('   Example $', sys.argv[0], TOPICS[0])
            print('')
            sys.exit()
    else:
        comkey = '*'
    return comkey


def get_frames(comkey):
    """ Fetch all frame files and put them in frames directory. """
    logger.info('Topic Group: {}'.format(browser.title))

    # Fetch frames one at a time until no more found
    more_pages = True
    while more_pages:
        base_name = "{}.html".format(frame.frame_id())
        frame_name = os.path.join(FRAMESDIR, base_name)
        logger.info('Creating {}'.format(frame_name))
        frame.write_page(frame_name)
        more_pages = frame.next_page()

    return None


def remove_old_frames():
    """ remove all previous HTML frame files """
    for filename in os.listdir(FRAMESDIR):
        file_path = os.path.join(FRAMESDIR, filename)
        try:
            if (os.path.isfile(file_path)
                    and filename.endswith('.html')):
                os.unlink(file_path)
        except Exception as e:
            failure = 'Failed to delete {}'.format(file_path)
            print('{} {}'.format(failure, e))
            logger.warning(failure)
    return None


if __name__ == "__main__":
    # Parse input parameters and setup logging -- DEFAULT
    logsys = logSystem(sys.argv)
    logger = logsys.setup(__name__)
    comkey = get_parms(sys.argv)

    # If the ./frames subdirectory does not already exist, create it
    # otherwise if we are doing all topics, remove all previous frames
    os.makedirs(FRAMESDIR, exist_ok=True)   # store in sub-directory
    if comkey == '*':
        remove_old_frames()

    # Use Selenium to launch web browser to handle JavaScript
    browser = webdriver.Chrome()
    home = HomePage(browser, logger)
    home.login()

    # If no topic provided, process all topics
    frame = FramePage(browser, logger)
    if comkey == '*':
        for topic in TOPICS:
            frame.load_from_key(topic)
            get_frames(topic)
    else:
        frame.load_from_key(comkey)
        get_frames(comkey)

    # Use Selenium to shutdown Firefox browser
    browser.quit()
    print('Done.')
