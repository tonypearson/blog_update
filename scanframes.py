#!/usr/bin/env python3
# scanframes.py
# By Tony Pearson, IBM, July 2020
#
# Reads all of the frame files collected by getframes.py
# and creates postlist.txt
#
# Usage:
#       ./getposts.py               This option will delete all previous posts
#       ./getposts.py fla           Process fla00001 to fla99999 frames
#       ./getposts.py fla00007      Process just the flash007 frame

import os
import re
import requests
import sys
from selenium import webdriver
from bs4 import BeautifulSoup
from functions import get_modname, setup_logging
from pageClass import HomePage, PostPage, FRAMESDIR, POSTSDIR, PARSER
from showProgress import showProgress


BLOGID = re.compile(r'Tony[ ]?Pearson')
LASTDATE = {}
DATEregex = re.compile(r'/(20\d\d/[01]\d/[0-3]\d)/')
FRAME_DATE = 'Last date for {} is {}'
FRAME_SEQ = 'Blog {} after Topic {} Last Date {}'
BLOGLINK = 'tony-pearson1'

def get_parms(argv):
    modname = get_modname(argv)

    # Allow individual keyword that can match the frames file
    # Examples:  flash (all flashNNN) or flash007 (just this frame)
    if len(argv) > 1:
        keyw = argv[1]
    else:
        keyw = '.'   # matches all files
    return modname, keyw

def parse(framename):
    """ Parse the frame to extract all post links """
    topic = re.sub(r'.*/(\w*).html', r'\1', framename)
    print(topic, end='')
    logger.info('Topic={} Name={}'.format(topic,framename))
    soup = BeautifulSoup(open(framename), PARSER)
    links = soup.findAll('a', attrs={'class': 'BlogTitle'})

    # A frame can list up to 20 blog posts
    dot = showProgress()
    for link in links:
        postlink = link['href']
        # import pdb; pdb.set_trace()
        dot.show()
        if BLOGLINK not in postlink:
            logger.info('Ignoring: {}'.format(postlink))
            continue

        mo = DATEregex.search(postlink)
        if mo:
            blogdate = mo.group(1)
            if topic not in LASTDATE:
                LASTDATE[topic] = blogdate
                logger.info(FRAME_DATE.format(topic,blogdate))
            elif LASTDATE[topic] < blogdate:
                warn_seq = FRAME_SEQ.format(blogdate, topic, LASTDATE[topic])
                logger.warning(warn_seq)
                continue
            print(topic, postlink, file=out_file)
    dot.end()
    return None


if __name__ == "__main__":
    modname, keyw = get_parms(sys.argv)
    logger = setup_logging(__name__, modname)

    with open('postlist.txt', 'w') as out_file:
        filenames = sorted(os.listdir(FRAMESDIR))
        for filename in filenames:
            # Only process HTML files in this directory
            if ((keyw < filename)
                    and filename.endswith('.html')):
                framename = os.path.join(FRAMESDIR, filename)
                logger.info('Processing: {}'.format(framename))
                parse(framename)

    print('Done')
