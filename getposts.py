#!/usr/bin/python3
# getposts.py
# By Tony Pearson, IBM, July 2020
#
# Reads all of the frame files collected by getframes.py
# and fetches all posts that belong to Tony Pearson
#
# Usage:
#       ./getposts.py               This option will delete all previous posts
#       ./getposts.py flash         Process flash001 to flash999 frames
#       ./getposts.py flash007      Process just the flash007 frame

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
            follow(postlink, topic)
    dot.end()
    return None


def follow(postlink, topic):
    """ Fetch post content and check meta data """
    post_page = PostPage(browser, logger)
    logger.debug('Attempting: {}'.format(postlink))
    try:
        post_page.from_url(postlink)
    except:
        return None
    # import pdb; pdb.set_trace()
    desc, byline = post_page.author()
    # print('DESC:', desc, 'BYLINE:', byline)

    post = post_page.soup
    belongs_to_blogger = False

    # Older posts use meta tag description, newer posts use byline
    if desc:
        content = desc['content'].split('\n')
        postedby = content[0]
        logger.info(postedby)
        if BLOGID.search(postedby):
            belongs_to_blogger = True
    else:
        if BLOGID.search(byline.text):
            belongs_to_blogger = True

    if belongs_to_blogger:
        post_page.permalink_from_source(post)
        postname = make_name(post_page.url, topic)
        post_page.write_page(postname)
        logger.info('Tony: {}'.format(postname))
    return None


def make_name(linkurl, topic):
    """ generate file name from permalink in POSTSDIR directory """
    fileRegex = re.compile(r'^(.*)/(20\d\d)/(\d\d)/(\d\d)/(.*)$')
    mo = fileRegex.search(linkurl)
    date_part = mo.group(2)+'-'+mo.group(3)+'-'+mo.group(4)
    gen_name = date_part+'-'+topic+'-'+mo.group(5)+'.html'
    filename = os.path.join(POSTSDIR, gen_name)
    return filename


def remove_old_posts(keyw):
    """ remove all previous HTML frame files """
    for filename in os.listdir(POSTSDIR):
        file_path = os.path.join(POSTSDIR, filename)
        try:
            if (os.path.isfile(file_path)
                    and (keyw in filename)
                    and filename.endswith('.html')):
                os.unlink(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
    return None


if __name__ == "__main__":
    modname, keyw = get_parms(sys.argv)
    logger = setup_logging(__name__, modname)

    os.makedirs(POSTSDIR, exist_ok=True)
    # remove_old_posts(keyw)

    filenames = sorted(os.listdir(FRAMESDIR))
    for filename in filenames:
        # Only process HTML files in this directory
        if ((keyw < filename)
                and filename.endswith('.html')):
            framename = os.path.join(FRAMESDIR, filename)
            logger.info('Processing: {}'.format(framename))
            parse(framename)

    print('Done')
