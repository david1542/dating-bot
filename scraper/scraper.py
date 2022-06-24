from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from controllers.bumble import BumbleController
from controllers.okcupid import OKCupidController

profile_path = '/Users/dudulasry/Library/Application Support/Firefox/Profiles/8v96evl6.default-release'

firefox_options = Options()
firefox_options.add_argument("-profile")
firefox_options.add_argument(profile_path)

driver = webdriver.Firefox(options=firefox_options)

# bumble = BumbleController(driver)
# bumble.login()
# bumble.scrape()

okcupied = OKCupidController(driver)
okcupied.login()
okcupied.scrape()