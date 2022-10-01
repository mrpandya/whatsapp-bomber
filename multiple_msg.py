from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

import os


class WhatsApp:
    def __init__(self) -> None:
        user = os.getlogin()

        options = webdriver.ChromeOptions()

        options.add_argument('--profile-directory=Default')
        options.add_argument(
            f'--user-data-dir=C:\\Users\\{user}\\AppData\\Local\\Google\\Chrome\\User Data')

        PATH = os.path.dirname(__file__) + "\\chromedriver.exe"
        self.driver = webdriver.Chrome(
            executable_path=PATH, chrome_options=options)

        self.driver.get("https://web.whatsapp.com")
        WebDriverWait(self.driver, 5000).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="side"]/header/div[2]/div/span/div[2]/div')))

    def send_msg(self, phone: str, msg: str):
        url = "https://web.whatsapp.com/send?phone=" + phone + "&text=" + msg + "&app_absent=1"
        self.driver.get(url)
        enter_action = ActionChains(self.driver)
        enter_action.send_keys(Keys.ENTER)
        # Send message
        enter_action.perform()


    def END(self):
        # check the message sended
        WebDriverWait(self.driver, 9000).until(
            EC.invisibility_of_element_located((By.XPATH, '//span[@data-icon="status-time"]')))
        sleep(3)
        self.driver.close()
