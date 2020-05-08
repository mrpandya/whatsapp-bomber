from selenium import webdriver 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By 
import time 
driver = webdriver.Chrome('/home/manan/Desktop/fithit/chromedriver') 
driver.get("https://web.whatsapp.com/") 
wait = WebDriverWait(driver, 600) 
target = '"Garam masala"' 
string = "garam masala forever"
x_arg = '//span[contains(@title,' + target + ')]'
group_title = wait.until(EC.presence_of_element_located((By.XPATH, x_arg))) 
group_title.click() 

for i in range(200):
    element=driver.find_element_by_css_selector("div[data-tab='1']")
    element.send_keys(string+Keys.ENTER)
