#!/usr/bin/python3
# chktopic.py -- Check if post is in the right topic group
# By Tony Pearson, IBM, 2020
#
import os
import re
import operator
import sys
from bs4 import BeautifulSoup
from constants import POSTSDIR, PARSER
from functions import get_modname, setup_logging
from pageClass import PostPage

UNITTEST = False
VERBOSE = False
NAMERegex = re.compile(r'/[-0123456789]*([a-z]*)[0-9]')
Tmatch = 'Tmatch: {} {} {}'
Fmatch = 'Fmatch: {} {} {}'
POSTEDbyRegex = re.compile(r'posted by: (.*)$')
LOGMSG = 'Author:{} Postname:{} Permalink:{}'

TOPICS = {'dpr':   [re.compile(r'ADSTAR'),
                    re.compile(r'ADSM'),
                    re.compile(r'Tivoli[\s]+Storage[\s]+Manager'),
                    re.compile(r'Spectrum[\s]+Protect'),
                    re.compile(r'SPTA'),
                    re.compile(r'Technical Advisor'),
                    re.compile(r'Actifio'),
                    re.compile(r'Veritas'),
                    re.compile(r'NetBackup'),
                    re.compile(r'Commvault'),
                    re.compile(r'[bB]ackup'),
                    re.compile(r'achiv(e|ing)'),
                    re.compile(r'BaaS'),
                    re.compile(r'\WILM'),
                    re.compile(r'[iI]nformation\s+[lL]ifecycle\s+[mM]anage'),
                    re.compile(r'[cC]ompliance'),
                    re.compile(r'[rR]egulat(ion|ory)'),
                    re.compile(r'[rR]ecover(y|ing)'),
                    re.compile(r'[rR]estor(e|ing)'),
                    re.compile(r'Business[\s]+Continuity'),
                    ],
            'fla': [re.compile(r'A9000'),
                    re.compile(r'[aA]ll-flash'),
                    re.compile(r'FlashSystem'),
                    re.compile(r'\WSSD'),
                    re.compile(r'[sS]Solid[-\s]+[sS]tate'),
                    re.compile(r'EMC\W'),
                    re.compile(r'Celerra'),
                    re.compile(r'CLARiiON'),
                    re.compile(r'Storwize'),
                    re.compile(r'NAND'),
                    re.compile(r'NVMe'),
                    re.compile(r'[fF]irmware'),
                    re.compile(r'\WXIV'),
                    re.compile(r'[mM]odel 314'),
                    re.compile(r'[SD]RAM'),
                    re.compile(r'RAMSan'),
                    re.compile(r'RAID'),
                    re.compile(r'Spectrum[\s]+Accelerate'),
                    re.compile(r'Spectrum[\s]+Virtualize'),
                    re.compile(r'SAN[\s]+Volume[\s]+Controller'),
                    re.compile(r'[sS]torage\s+[vV]irtualization'),
                    re.compile(r'SVC'),
                    re.compile(r'Texas[\s]+Memory[\s]+Systems'),
                    ],
          'fob':   [re.compile(r'GPFS'),
                    re.compile(r'\WCOS'),
                    re.compile(r'Spectrum[\s]+Scale'),
                    re.compile(r'\WNAS'),
                    re.compile(r'\WCIFS'),
                    re.compile(r'\WNFS'),
                    re.compile(r'ATMOS'),
                    re.compile(r'Isilon'),
                    re.compile(r'[oO]bject[\s]+[sS]torage'),
                    re.compile(r'[cC]loud[\s]+[sS]torage'),
                    re.compile(r'Ceph'),
                    re.compile(r'\WESS'),
                    re.compile(r'Elastic[\s]+Storage[\s]+Server'),
                    re.compile(r'Amazon[\s]+S3'),
                    re.compile(r'Clever[sS]afe'),
                    re.compile(r'\WCAS\W'),
                    re.compile(r'[cC]ontent[ -][aA]ddressable'),
                    ],
          'mfr':   [
                    re.compile(r'DS8[013]00'),
                    re.compile(r'DS8[789]\d\d'),
                    re.compile(r'TS7\d\d\d'),
                    re.compile(r'Symmetrix'),
                    re.compile(r'ChuckH'),
                    re.compile(r'Hollis'),
                    re.compile(r'Yoshida'),
                    re.compile(r'\WHDS'),
                    re.compile(r'Hitachi'),
                    ],
          'san':   [re.compile(r'[bB]luetooth'),
                    re.compile(r'[eE]thernet'),
                    re.compile(r'Infiniband'),
                    re.compile(r'iSCSI'),
                    re.compile(r'TCP/IP'),
                    re.compile(r'Brocade'),
                    re.compile(r'Broadcom'),
                    re.compile(r'Cisco'),
                    re.compile(r'[SL]AN\W'),
                    re.compile(r'[cC]onnectivity'),
                    re.compile(r'B-type'),
                    re.compile(r'FCIP'),
                    re.compile(r'(Storage|Local|Metro)\s+Area\s+Network'),
                    re.compile(r'VersaStack'),
                    re.compile(r'[cC]onverged'),
                    re.compile(r'[wW]iring'),
                    ],
          'smr':   [re.compile(r'Spectrum Software'),
                    re.compile(r'[sS]oftware[-\s]+[dD]efined'),
                    re.compile(r'Spectrum[\s]+Control'),
                    re.compile(r'Spectrum[\s]+Connect'),
                    re.compile(r'Spectrum[\s]+Discover'),
                    re.compile(r'Storage[\s]+Insights'),
                    re.compile(r'Productivity[\s]+Center'),
                    re.compile(r'ITIL'),
                    ],
          'tap':  [re.compile(r'\W[tT]ape'),
                    re.compile(r'[cC]artridge'),
                    re.compile(r'Data[\s]+Domain'),
                    re.compile(r'TS[1234]\d\d\d'),
                    re.compile(r'LTO'),
                    re.compile(r'Linear[\s]+Tape[\s]+Open'),
                    re.compile(r'Ultrium'),
                    re.compile(r'LTFS'),
                    re.compile(r'Spectrum[\s]+Archive'),
                    re.compile(r'[vV]irtual[\s]+[tT]ape'),
                    re.compile(r'\WVTL'),
                    re.compile(r'\WATL'),
                    re.compile(r'[aA]ir[-\s][gG]ap')
                    ],
          }


class TopicError(RuntimeError):
    pass


def parse(postname):
    """ Parse the post to extract all words """
    counts = {}
    numgroups = 0
    for topic in TOPICS:
        counts[topic] = 0
        numgroups += 1

    mo = NAMERegex.search(postname)
    if mo is None:
        logmsg = 'Error, unable to determine topic of post'
        logger.error(logmsg + ': ' + postname)
        raise TopicError(logmsg)

    this_topic = mo.group(1)
    import pdb; pdb.set_trace()
    soup = BeautifulSoup(open(postname), PARSER)
    title_contents = get_title(soup)
    file_contents = get_contents(soup)
    blogger = get_blogger(soup)
    permalink = get_permalink(soup)

    for topic, patterns in TOPICS.items():
        for pattern in patterns:
            mo = pattern.search(title_contents)
            if mo:
                logger.info(Tmatch.format(topic, pattern, mo.group()))
                counts[topic] += 3
            mo = pattern.search(file_contents)
            if mo:
                logger.info(Fmatch.format(topic, pattern, mo.group()))
                counts[topic] += 1

    tsort = sorted(counts.items(), key=operator.itemgetter(1), reverse=True)
    top_topic = tsort[0][0]
    if (top_topic != this_topic
            and counts[top_topic] == counts[this_topic]):
        top_topic = this_topic
        for n in range(1, numgroups):
            if tsort[n][0] == this_topic:
                # Swap positions to put current topic first
                tsort[0], tsort[n] = tsort[n], tsort[0]
                break

    stats = ''
    for group in tsort:
        stats += group[0]+" "+str(group[1])+" "

    if counts[top_topic] > counts[this_topic]:
        action = 'MOVE'
    elif tsort[0][1] == tsort[1][1]:
        action = 'EVAL'
    else:
        action = 'KEEP'

    logger.info(LOGMSG.format(blogger, postname, permalink))
    print(action, stats, permalink, file=output_file)
    return top_topic


def get_title(soup):
    """ get the title of post """
    title_contents = ''
    title_elem = soup.find('h3', attrs={'class': 'blogTitle'})
    if title_elem:
        title_contents = title_elem.text.replace('</h3>', '')
        title_contents.replace('\n', ' ')
    return title_contents


def get_contents(soup):
    """ get the post contents, minus all the boilerplate """
    file_contents = ''
    divs = soup.findAll('div', attrs={'class': 'col-md-12'})
    if divs:
        for div in divs:
            paragraphs = div.findAll('p')
            for paragraph in paragraphs:
                file_contents += ' '+paragraph.text
            paragraphs = div.findAll('table')
            for paragraph in paragraphs:
                file_contents += ' '+paragraph.text
            paragraphs = div.findAll('dl')
            for paragraph in paragraphs:
                file_contents += ' '+paragraph.text

    file_contents.replace('\n', ' ')
    return file_contents


def get_blogger(soup):
    """ get blogger id or name """

    desc = soup.find('meta', attrs={'name': 'description'})
    byline_id = 'MainCopy_ctl04_ucPermission_UserName_lnkProfile'
    byline = soup.find('a', attrs={'id': byline_id})
    blogger = ''
    if desc:
        content = desc['content'].split('\n')
        postedby = content[0]
        mo = POSTEDbyRegex.search(postedby)
        if mo:
            blogger = mo.group(1)
    else:
        
        if byline:
            blogger = byline.text
    return blogger


def get_permalink(soup):
    """ find permalink within post content """
    block = soup.find('div', attrs={'class': 'permalink-block'})
    inside = block.find('input')
    permalink = inside['value']
    return permalink


if __name__ == "__main__":
    modname = get_modname(sys.argv)
    logger = setup_logging(__name__, modname)

    posts = {}
    for topic in TOPICS:
        posts[topic] = 0

    output_file = open('reclassify.txt', 'w')

    filenames = sorted(os.listdir('./' + POSTSDIR))
    for filename in filenames:
        # Only process HTML files in this directory
        if (filename.startswith('20')
                and filename.endswith('.html')):
            postname = os.path.join(POSTSDIR, filename)
            logger.info('Processing: ' + postname)
            top_topic = parse(postname)
            posts[top_topic] += 1

    print("Done.")
