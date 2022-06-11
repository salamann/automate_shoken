import yaml
from time import sleep
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

def read_config(file_name='config.yaml'):
    with open(file_name, 'r', encoding='utf-8') as f:
        configs = yaml.safe_load(f)
    return configs

def signin(url, used_id, password, second_password):
    # headless mode
    # option = Options()
    # option.add_argument('--headless')
    # driver = webdriver.Chrome(options=option)

    # normal mode
    driver = webdriver.Chrome()

    driver.get(url)
    user_card_no = driver.find_element(by=By.NAME, value="user_id")
    user_card_no.send_keys(used_id)
    user_password = driver.find_element(by=By.NAME, value="user_password")
    user_password.send_keys(password)
    signin_button = driver.find_element(by=By.NAME, value="ACT_login")
    signin_button.click()

    sleep(3)
    # hit the portfolio button
    a_elements = driver.find_elements(by=By.TAG_NAME, value='a')
    for a_element in a_elements:
        try:
            img = a_element.find_element(by=By.TAG_NAME, value='img')
            alt = img.get_attribute('alt')
            # print(alt)
            if alt == 'ポートフォリオ':
                portfolio_url = a_element.get_attribute('href')
                driver.get(portfolio_url)
                break
        except NoSuchElementException:
            pass

    # hit the sell button
    tr_elements = driver.find_elements(by=By.TAG_NAME, value='tr')
    for tr_element in tr_elements:
        td_elements = tr_element.find_elements(by=By.TAG_NAME, value='td')
        for td_element in td_elements:
            if '全世界株式' in td_element.text:
            # if '国内債券インデックス' in td_element.text:
                a_elements = tr_element.find_elements(by=By.TAG_NAME, value='a')
                for a_element in a_elements:
                    if '売却' in a_element.text:
                        sale_url = a_element.get_attribute('href')
                        driver.get(sale_url)
                        break
            else:
                continue
            break
        else:
            continue
        break

    # fill the blanks and hit the sell button
    radio_button = driver.find_element(by=By.ID, value='buy_sell_202')
    radio_button.click()
    # password_field = driver.find_element(by=By.ID, value='pwd1')
    # password_field.send_keys()
    # password_field = driver.find_element(by=By.ID, value='pwd2')
    # password_field.send_keys()
    password_field = driver.find_element(by=By.ID, value='pwd3')
    password_field.send_keys(second_password)
    # password_field = driver.find_element(by=By.ID, value='pwd4')
    # password_field.send_keys()
    check_box = driver.find_element(by=By.NAME, value='skip_estimate')
    check_box.click()
    # radio_button = driver.find_element(by=By.NAME, value='ACT_place')
    # radio_button.click()
    sleep(120)



if __name__=="__main__":
    configs = read_config()
    signin(configs['sbi']['url'], configs['sbi']['user_id'], configs['sbi']['password'],
    configs['sbi']['second_password'])
    pass