import os
import logging
import requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

FRAMESDIR = 'frames'
POSTSDIR = 'posts'
PARSER = 'lxml'

class LoginError(RuntimeError):
    pass


class EditError(RuntimeError):
    pass


class BasePage(object):
    """Base class to initialize browser page"""

    def __init__(self, driver, logger):
        self.driver = driver
        self.driver.implicitly_wait(60)
        self.driver.set_page_load_timeout(120)

        self.pagename = 'BasePage'
        self.logger = logger
        self.url = ''

    def screenshot(self, index):
        shotname = 'screen-' + self.pagename + index + '.png'
        self.driver.get_screenshot_as_file(shotname)

    def write_page(self, filename):
        source = self.driver.page_source
        """ write the page source to file """
        with open(filename, 'wb') as file_obj:
            file_obj.write(source.encode(encoding='utf-8'))
        return self


class HomePage(BasePage):
    """ Home page for IBM Storage Community """

    def __init__(self, driver, logger):
        super().__init__(driver, logger)
        self.url = 'https://community.ibm.com/community/user/storage/home'
        self.credentials = 'login_credentials.key'
        self.pagename = 'HomePage'

    def _click_signin(self):
        browser = self.driver
        wait = WebDriverWait(browser, 10)
        action1 = ActionChains(browser)
        menuloc = (By.CSS_SELECTOR, ".ft-user")
        menu = wait.until(EC.presence_of_element_located(menuloc))
        action1.move_to_element(menu).click_and_hold(on_element=menu).perform()
        self.screenshot('01')
        browser.find_element_by_link_text('Sign In').click()
        wait.until(EC.staleness_of(menu))
        return None

    def _enter_username(self, uid):
        browser = self.driver
        wait = WebDriverWait(browser, 10)
        self.screenshot('02')
        userfield = browser.find_element_by_id('username')
        userfield.send_keys(uid)
        browser.find_element_by_id('continue-button').click()
        wait.until(EC.staleness_of(userfield))
        return None

    def _enter_password(self, pwd):
        browser = self.driver
        # import pdb; pdb.set_trace()
        wait = WebDriverWait(browser, 10)
        self.screenshot('03')
        pwdfield = browser.find_element_by_id('password')
        pwdfield.send_keys(pwd)

        # With chrome, sending keys is enough, for Firefox click sign-in
        if not isinstance(browser, webdriver.chrome.webdriver.WebDriver):
            browser.find_element_by_id('signinbutton').click()
            wait.until(EC.staleness_of(pwdfield))
        return None

    def _auto_login(self):
        """ if credits file exists, use it to login automatically """
        entries = []
        with open(self.credentials, 'r') as cred_file:
            line = cred_file.readline()
            while line:
                entries.append(line)
                line = cred_file.readline()
        if len(entries) == 2:
            self._click_signin()
            self._enter_username(entries[0])
            self._enter_password(entries[1])
        else:
            raise LoginError('Invalid credentials')
        return

    def login(self):
        """ automatically or manually log in """
        self.logger.debug('HomeURL: {}'.format(self.url))
        self.driver.get(self.url)
        signed_in = False
        if os.path.exists(self.credentials):
            try:
                self._auto_login()
                signed_in = True
            except LoginError:
                signed_in = False

        if not signed_in:
            print(' ')
            print('On web browser, use upper right button to')
            print('   Sign In with your IBMid and password.')
            input('Press ENTER here after you have manually signed in ')
        return self


EDIT_ID = 'MainCopy_ctl04_ucPermission_ManageDropDown1_lnkbtnEdit'
TITLE_ID = 'PageTitleH1'


class PostPage(BasePage):
    """ Home page for IBM Storage Community """

    def __init__(self, driver, logger):
        super().__init__(driver, logger)
        self.pagename = 'PostPage'
        self.content = ''
        self.soup = ''

    def from_file(self, filename):
        self.permalink(filename)
        self.from_permalink(self.url)
        return self

    def from_permalink(self, permalink):
        self.url = permalink
        browser = self.driver
        try:
            browser.get(self.url)
        except TimeoutException as e:
            self.logger.warning(permalink + ':' + e)
        wait = WebDriverWait(browser, 10)
        wait.until(EC.presence_of_element_located((By.ID, TITLE_ID)))
        self.content = browser.page_source
        self.soup = BeautifulSoup(self.content, PARSER)
        return self

    def from_url(self, url):
        self.url = url
        r = requests.get(url)
        self.content = r.content
        self.soup = BeautifulSoup(self.content, PARSER)
        return self

    def author(self):
        if self.soup == '':
            self.soup = BeautifulSoup(self.content, PARSER)
        post = self.soup

        # Older posts use meta tag description, newer posts use byline
        desc = post.find('meta', attrs={'name': 'description'})
        byline_id = 'MainCopy_ctl04_ucPermission_UserName_lnkProfile'
        byline = post.find('a', attrs={'id': byline_id})
        return desc, byline

    def editpost(self):
        browser = self.driver
        wait = WebDriverWait(browser, 10)
        try:
            edit_button = browser.find_element_by_id(EDIT_ID)
            edit_button.click()
            wait.until(EC.staleness_of(edit_button))
        except Exception:
            raise EditError('Unable to edit file')
        return self

    def permalink(self):
        if self.soup == '':
            self.soup = BeautifulSoup(self.content, PARSER)
        post = self.soup
        self.permalink_from_source(post)
        return self

    def permalink_from_source(self, post):
        block = post.find('div', attrs={'class': 'permalink-block'})
        inside = block.find('input')
        self.url = inside['value']
        return self

    def permalink_from_file(self, postname):
        post = BeautifulSoup(open(postname), PARSER)
        self.permalink_from_source(post)
        return self


COMKEYS = {
    'dpr': '2437e98f-10ca-4898-ae8c-c7f0d6e42e59',           # Data Protection
    'fob': '1142f81e-95e4-4381-95d0-7977f20d53fa',   # File and object storage
    'fla': '259eb30e-f20d-4433-aa35-ff2bc9bf625f',             # Flash Storage
    'mfr': 'c6644533-459d-4dc4-af5e-9c9f04f4f4c7',         # Mainframe Storage
    'san': '8c5ad67f-4f4b-478a-8deb-6a219c72dfab',     # Storage Area Networks
    'smr': '295787b1-a4e4-43ff-9bfe-206a7912b51d',     # Storage Mgt/Reporting
    'tap': '85531a8a-8971-4c0e-8d2b-098ba927269e',              # Tape Systems
    }

COMFRAME = ('https://community.ibm.com/community/user/storage/' 
            + 'communities/community-home/recent-community-blogs'
            + '?communitykey={}&tab=recentcommunityblogsdashboard')

class FramePage(BasePage):
    """ Home page for IBM Storage Community """

    def __init__(self, driver, logger):
        super().__init__(driver, logger)
        self.pagename = 'FramePage'
        self.key = ''

    def load_from_key(self, comkey):
        self.url = COMFRAME.format(COMKEYS[comkey])
        self.logger.debug('FrameURL: {}'.format(self.url))
        self.key = comkey
        browser = self.driver
        wait = WebDriverWait(browser, 10)
        browser.get(self.url)
        wait.until(EC.presence_of_element_located((By.ID, 'PageTitleH1')))
        return self

    def frame_id(self):
        browser = self.driver
        currentp = browser.find_element_by_class_name('CurrentPageLabel')
        # Format this so AAAnnnnn always 8 characters long
        # Where AAA is frame identifier, and nnnnn is frame number 001 to 999
        pagenum = currentp.text.rjust(8 - len(self.key), '0')
        base_name = self.key + pagenum
        return base_name

    def next_page(self):
        browser = self.driver
        buttons = browser.find_element_by_class_name('pagination')
        nextpage = browser.find_element_by_link_text('»')
        page_found = False
        if nextpage.is_enabled():
            try:
                # Click on the » button, wait until previous frame stale
                nextpage.click()
                WebDriverWait(browser, 10).until(EC.staleness_of(buttons))
                page_found = True
            # On last page, the above will time-out
            except TimeoutException:
                page_found = False
        return page_found
