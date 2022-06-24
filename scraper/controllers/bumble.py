import logging

import urllib.request
import uuid
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver

from constants import BUMBLE_URL, BASE_IMAGES_PATH
from utils import find_element, find_elements

class BumbleController:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        
    def login(self):
        main_window_id = self.driver.current_window_handle
        self.driver.get(BUMBLE_URL)

        join_button = find_element(self.driver, By.LINK_TEXT, 'Join')
        join_button.click()

        # facebook_button = find_element(self.driver, By.CLASS_NAME, 'color-provider-facebook')
        # facebook_button.click()

        # new_window_id = self.driver.window_handles[1]
        # self.driver.switch_to.window(new_window_id)

        # email_input = find_element(self.driver, By.ID, 'email')
        # password_input = find_element(self.driver, By.ID, 'pass')
        # submit_button = find_element(self.driver, By.NAME, 'login')

        # email_input.send_keys(FACEBOOK_CREDENTIALS['email'])
        # password_input.send_keys(FACEBOOK_CREDENTIALS['pass'])
        # submit_button.click()

        # self.driver.switch_to.window(main_window_id)
    
    def scrape(self):
        action_items = find_elements(self.driver, By.CLASS_NAME, 'encounters-controls__action')
        pass_button = action_items[-1]

        should_continue = True
        while should_continue:
            try:
                self._scrape_current_profile()
                pass_button.click()
            except:
                should_continue = False
        
        
    def _scrape_current_profile(self):
        profile_name_class = 'encounters-story-profile__name'
        story_container_class = 'encounters-album__story'
        image_class = 'media-box__picture-image'

        profile_name = find_element(self.driver, By.CLASS_NAME, profile_name_class).text.lower()
        profile_id = f'{str(uuid.uuid4())}_{profile_name}'
        profile_path = os.path.join(BASE_IMAGES_PATH, profile_id)
        
        # Create directory for profile that'd store the photos
        os.mkdir(profile_path)

        # Collect images
        chapters = find_elements(self.driver, By.CLASS_NAME, story_container_class)
        for i, chapter in enumerate(chapters):
            try:
                image = chapter.find_element(By.CLASS_NAME, image_class)
            except:
                continue
            
            image_url = image.get_attribute('src')
            image_path = os.path.join(profile_path, f'{profile_id}_{i}.png')

            # Download image
            urllib.request.urlretrieve(image_url, image_path)

