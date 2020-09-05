#!/usr/bin/python3
# movepost.py -- Move posts to new topic group
# By Tony Pearson, IBM, 2020
#
import os
import re
import operator
import sys
import time
import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from functions import get_modname, setup_logging
from pageClass import HomePage, PostPage, EDIT_ID, TITLE_ID
from showProgress import showProgress

TOPICS = {
    'dpr': 'Data Protection Software',                # Modern Data Protection
    'fla': 'Flash Storage',                                   # Flash Storage
    'fob': 'File and Object Storage',                # File and object storage
    'mfr': 'Mainframe Storage',                            # Mainframe storage
    'san': 'Storage Area Networks (SAN)',              # Storage Area Networks
    'smr': 'Storage Management and Reporting',      # Software Defined Storage
    'tap': 'Tape Storage',                                      # Tape Systems
}
URL = 'https://community.ibm.com/community/user/storage/home'
LINEregex = re.compile(r'^(MOVE) (tap|fla|fob|dpr|mfr|san|smr) .* (http.*)')
PARSER = 'lxml'
SELECT_ID = 'MainCopy_ctl04_CommunityList'
SCROLL_DOWN = "window.scrollTo(0, document.body.scrollHeight);"
SEO_ID = 'MainCopy_ctl04_hypHideSeo'
FOOTER = 'modal-footer'
SAVE_ID = 'MainCopy_ctl04_btnSaveEditedBlog'
VERBOSE = True


def get_parms(argv):
    """ get parameters passed in from command line """
    modname = get_modname(argv)
    if len(argv) < 2:
        movename = 'reclassify.txt'
    else:
        movename = argv[1]
    return modname, movename


def move_post(topic, permalink):
    """ edit post to move it to new topic group """
    page_post = PostPage(browser, logger)
    page_post.from_permalink(permalink)

    try:
        heading = browser.find_element_by_id(TITLE_ID)
        if heading == topic:
            logger.info('Already {} {}'.format(topic,permalink))
            return 1
    except Exception as e:
        logger.warning('Unable to find heading {}'.format(permalink))
        return 0

    logger.info('Moving: {} to {}'.format(permalink, topic))
    wait = WebDriverWait(browser, 10)
    try:
        wait.until(EC.element_to_be_clickable((By.ID, EDIT_ID)))
        edit_button = browser.find_element_by_id(EDIT_ID)
    except Exception:
        logger.info('Unable to Edit this post')
        return 0
    edit_button.click()
    wait = WebDriverWait(browser, 10)
    wait.until(EC.staleness_of(edit_button))
    time.sleep(2)
    scroll_down()
    update_topic_group(topic)
    time.sleep(2)

    for n in range(3):
        save_button = browser.find_element_by_id(SAVE_ID)
        try:
            save_button.click()
        except Exception as e:
            print('Exception caught:', n, str(e))
        else:
            break
        find_pulldown()
        time.sleep(2)

    return 1


def scroll_down():
    """ scroll down page so pull-down menu options visible """
    browser.execute_script(SCROLL_DOWN)
    time.sleep(2)
    return None


def find_pulldown():
    buttons = browser.find_elements_by_tag_name('button')
    pulldown = None
    for button in buttons:
        button_data_id = button.get_attribute('data-id')
        if button_data_id == SELECT_ID:
            pulldown = button
            break
    pulldown.click()
    time.sleep(2)
    return None


def update_topic_group(topic):
    new_group = TOPICS[topic]
    logger.info("New Group: {}".format(new_group))
    # import pdb; pdb.set_trace()
    find_pulldown()

    spans = browser.find_elements_by_tag_name('span')
    elem = None
    for span in spans:
        if span.text == new_group:
            elem = span

    elem.click()
    time.sleep(2)
    selection = Select(browser.find_element_by_id(SELECT_ID))
    options = selection.all_selected_options
    num_selected = len(options)
    return None


def process_line(line):
    """ process move request """
    
    mo = LINEregex.search(line)
    if mo:
        action = mo.group(1)
        topic = mo.group(2)
        permalink = mo.group(3)
        if action == 'MOVE':
            if topic in TOPICS:
                done = move_post(topic, permalink)
                if done == 0:
                    redo.append(line)
                return done
            else:
                logger.info('Unrecognized topic group: {}'.format(topic))
    return 0


def make_logname(stem):
    today = datetime.datetime.now()
    today_date = str(today.date())
    today_time = str(today.time())
    unique_name = (today_date[5:10] + '_'
                   + today_time[0:2]+today_time[3:5]
                   + "_" + stem + ".log")
    return(unique_name)


if __name__ == "__main__":
    modname, movename = get_parms(sys.argv)
    logger = setup_logging(__name__, modname)

    # Use Selenium to launch browser

    browser = webdriver.Chrome()
    storage_community = HomePage(browser, logger).login()

    lines_read, posts_moved = 0, 0
    redo = []
    dot = showProgress()
    with open(movename, 'r') as in_file:
        lines = in_file.read().splitlines()
        lines_read = len(lines)
        for line in lines:
            dot.show()
            posts_moved += process_line(line)

    if redo:
        logger.info('Retrying {} lines'.format(len(redo)))
        for line in redo:
            dot.show()
            posts_moved += process_line(line)

    dot.end()
    # Use Selenium to shutdown Firefox browser
    browser.quit()

    print(' ')
    print("Lines read:", lines_read, "Posts moved:", posts_moved)
    print("Done.")
