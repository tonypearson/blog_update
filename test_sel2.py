from selenium import webdriver

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


cap = DesiredCapabilities().FIREFOX

cap["marionette"] = False

browser = webdriver.Firefox(capabilities=cap, executable_path="/usr/bin/geckodriver")

browser.get('http://google.com/')

browser.quit()
