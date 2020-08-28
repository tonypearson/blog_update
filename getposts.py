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


def follow(postlink, topic):
    """ Fetch post content and check meta data """
    logger.debug('Attempting: {}'.format(postlink))
    r = requests.get(postlink)
    post = BeautifulSoup(r.content, PARSER)

    # import pdb; pdb.set_trace()
    
    desc = post.find('meta', attrs={'name': 'description'})
    byline_id = 'MainCopy_ctl04_ucPermission_UserName_lnkProfile'
    byline = post.find('a', attrs={'id': byline_id})
    # print('DESC:', desc, 'BYLINE:', byline)

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
        block = post.find('div', attrs={'class': 'permalink-block'})
        inside = block.find('input')
        permalink = inside['value']
        print(topic, permalink, file=perm_file)
        postname = make_name(permalink, topic)
        with open(postname, 'wb') as file_obj:
            file_obj.write(r.content)
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

    with open('permalink.txt', 'w') as perm_file:
        os.makedirs(POSTSDIR, exist_ok=True)
        dot = showProgress()
        with open('postlist.txt', 'r') as in_file:
            lines = in_file.read().splitlines()
            for line in lines:
                dot.show()
                topic, postlink = line.split(' ')
                follow(postlink, topic)
        dot.end()

    print('Done')
