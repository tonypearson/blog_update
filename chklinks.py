#!/usr/bin/python3
# chklinks.py -- Check links in all posts
# By Tony Pearson, IBM, 2020
#
import os
import re
import requests
import sys
from bs4 import BeautifulSoup
from pageClass import POSTSDIR, PARSER
from functions import get_modname, setup_logging

BLOGID = re.compile(r'Tony[ ]?Pearson')
STEMS = ['#',
         'mailto:',
         'javascript:',
         'participate/',
         'https://idaas.iam.ibm.com/',
         'https://www.ibm.com/products?',
         'https://www.ibm.com/community/',
         'https://community.ibm.com/',
         '/community/user/',
         'emcalendar',
         'http://www.higherlogic.com',
         'https://www.linkedin.com/company/',
         'https://twitter.com/',
         'https://www.ibm.com/privacy/',
         ]
DWORKS = 'https://www.ibm.com/developerworks/community/blogs/'
OLDBLOG = DWORKS + 'InsideSystemStorage/'


def parse(postname):
    """ Parse the post to extract all links """
    soup = BeautifulSoup(open(postname), PARSER)
    problems = []
    links = soup.select('a')
    for link in links:
        extlink = link.get('href')
        display_problems = False

        # Not all <a> tags have HREF links
        if extlink is None:
            display_problems = False
        # All links to IBM developerWorks need to be corrected
        elif extlink.startswith(DWORKS):
            display_problems = True
            code = 301
        # Eliminate boilerplate links, allow other links to be investigated
        elif allowlist(extlink):
            code = 404
            try:
                res = requests.get(extlink, timeout=5)
                code = res.status_code
            except Exception:
                code = 408
            if (code != requests.codes.ok):
                display_problems = True
        if display_problems:
            problems.append(str(code)+' '+extlink)

    # If problems with links found, print postname and list of problems
    if problems:
        print(postname, '-- problems found:', len(problems), file=out_file)
        for problem in problems:
            print('   ', problem, file=out_file)


def allowlist(extlink):
    """ Determine if further investigate necessary """
    for stem in STEMS:
        if extlink.startswith(stem):
            return False
    return True


if __name__ == "__main__":
    # Redirect all print statements to broken_links.txt file
    modname = get_modname(sys.argv)
    logger = setup_logging(__name__, modname)
    out_file = open('broken_links.txt', 'w')

    filenames = sorted(os.listdir(POSTSDIR))
    for filename in filenames:
        # Only process HTML files in this directory
        if filename.endswith('.html'):
            postname = os.path.join(POSTSDIR, filename)
            print('Processing:', postname)
            parse(postname)

    print("Done.")
