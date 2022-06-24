import os
import uuid
from selenium.webdriver.common.by import By
import urllib.request

from constants import BASE_IMAGES_PATH, OKCUPID_URL
from utils import find_element, find_elements

class OKCupidController:
    def __init__(self, driver):
        self.driver = driver

    def login(self):
        self.driver.get(OKCUPID_URL)

    def scrape(self):
        action_items = find_elements(self.driver, By.CLASS_NAME, 'dt-action-buttons-button-wrapper')
        pass_button = action_items[-1]

        should_continue = True
        while should_continue:
            try:
                self._scrape_current_profile()
                pass_button.click()
            except Exception as e:
                should_continue = False
        
        
    def _scrape_current_profile(self):
        profile_name_class = 'card-content-header__text'
        image_container_class = 'dt-photo'
        image_class = 'preloaded-image-content'

        profile_name = find_element(self.driver, By.CLASS_NAME, profile_name_class).text.lower()
        
        profile_id = f'{str(uuid.uuid4())}_{profile_name}'
        profile_path = os.path.join(BASE_IMAGES_PATH, 'okcupid', profile_id)
        
        # Create directory for profile that'd store the photos
        os.mkdir(profile_path)

        # Collect images
        chapters = find_elements(self.driver, By.CLASS_NAME, image_container_class)
        for i, chapter in enumerate(chapters):
            try:
                image = chapter.find_element(By.CLASS_NAME, image_class)
            except:
                continue
            
            style = image.get_attribute('style')
            image_url = style.split('"')[1]
            image_path = os.path.join(profile_path, f'{profile_id}_{i}.jpeg')

            # Download image
            urllib.request.urlretrieve(image_url, image_path)