import csv
import logging
import os
from typing import List

import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..common import BASE_DIR, get_chromedriver, get_user_agent

logging.basicConfig(level=logging.INFO)


class Hktvmall:
    STORAGE_PATH = os.path.join(BASE_DIR, '.storage')

    def __init__(self) -> None:
        self.url = 'https://www.hktvmall.com/hktv/zh/login'

    @property
    def phonenumbers(self) -> List[str]:
        phonenumber_file = os.path.join(self.STORAGE_PATH, 'raw_phonenumbers.txt')
        if os.path.isfile(phonenumber_file):
            phonenumbers = pd.read_csv(phonenumber_file, sep=",", header=None)[0].tolist()
            return phonenumbers
        else:
            raise Exception('The raw_phonenumbers.csv file does not exist in .stroage dirctory')

    def _go_to_login(self, wait: WebDriverWait) -> None:
        # wait for loading the login option by phonenumber and click it
        wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//*[@id='mainWrapper']/div/div[2]/div[1]/div[2]/div[2]/button"
        ))
        ).click()

    def _login(self, phone_number: str) -> bool:
        """
        Enters a phone number in main URL.
        """
        driver = get_chromedriver(user_agent=get_user_agent(), images=False, fast_load=False)
        wait = WebDriverWait(driver, 20)
        driver.get(self.url)

        try:
            self._go_to_login(wait)

            # wait for loading the phonenumber field and enter phonenumber
            driver.implicitly_wait(5)
            iframe = driver.find_element(
                By.XPATH,
                '//*[@id="cboxLoadedContent"]/iframe',
            )
            driver.switch_to.frame(iframe)
            driver.find_element(
                By.XPATH, '//*[@id="mainWrapper"]/div/div[1]/form/div[2]/input[2]'
            ).send_keys(phone_number)

            # click login(submit) button
            login_btn = driver.find_element(
                By.XPATH, '//*[@id="mainWrapper"]/div/div[1]/form/div[3]/button')
            login_btn.click()

        except Exception as e:
            logging.info(f'Raise exception while trying with {phone_number}: {e}')
            return False

        driver.implicitly_wait(5)
        try:
            driver.find_element(
                By.XPATH, '//*[@id="mainWrapper"]/div/div[1]/form/div[2]/div')
            return False
        except NoSuchElementException:
            return True

    def _remove_prefix(self, text: str, prefix: str = '852') -> str:
        if text.startswith(prefix):
            return text[len(prefix):]
        return text

    def main(self) -> str:
        valid_phonenumbers = []
        valid_phonenumber_file = os.path.join(self.STORAGE_PATH, 'valid_phonenumbers.csv')
        for phonenumber in self.phonenumbers:
            phonenumber = self._remove_prefix(str(phonenumber))
            is_logged = self._login(phonenumber)
            if is_logged:
                valid_phonenumbers.append(phonenumber)
        if valid_phonenumbers:
            with open(valid_phonenumber_file, 'w') as f:
                writer = csv.writer(f)
                writer.writerow(valid_phonenumbers)
