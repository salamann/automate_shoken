from ast import FunctionDef
import yaml
from time import sleep
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException


def read_config(file_name='config.yaml'):
    with open(file_name, 'r', encoding='utf-8') as f:
        configs = yaml.safe_load(f)
    return configs


def signin_sb(url, used_id, password, second_password):
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
    a_element = driver.find_element(by=By.XPATH,
                                    value="//a[img[@title='ポートフォリオ']]")
    a_element.click()

    fund_name_flake = "日本債権"
    tr_element = driver.find_element(by=By.XPATH,
                                     value=f'//tr[td[a[contains(text(), "{fund_name_flake}")]]]')
    a_element = tr_element.find_element(by=By.XPATH,
                                        value='//a[font[contains(text(), "売却")]]')
    a_element.click()

    # fill the blanks and hit the sell button
    radio_button = driver.find_element(by=By.ID, value='buy_sell_202')
    radio_button.click()
    password_field = driver.find_element(by=By.ID, value='pwd3')
    password_field.send_keys(second_password)
    check_box = driver.find_element(by=By.NAME, value='skip_estimate')
    check_box.click()
    # radio_button = driver.find_element(by=By.NAME, value='ACT_place')
    # radio_button.click()
    sleep(120)


def signin_rs(url, used_id, password, second_password):
    # headless mode
    # option = Options()
    # option.add_argument('--headless')
    # driver = webdriver.Chrome(options=option)

    # normal mode
    driver = webdriver.Chrome()

    driver.get(url)
    user_card_no = driver.find_element(by=By.ID, value="form-login-id")
    user_card_no.send_keys(used_id)
    user_password = driver.find_element(by=By.ID, value="form-login-pass")
    user_password.send_keys(password)
    signin_button = driver.find_element(by=By.ID, value="login-btn")
    signin_button.click()

    sleep(3)

    # hit 投資信託 button
    a_elements = driver.find_elements(by=By.TAG_NAME, value='a')
    for a_element in a_elements:
        if a_element.text == "投資信託":
            a_element.click()
            break

    # hit normal mode if it happens
    try:
        normal_mode_button = driver.find_element(
            by=By.CLASS_NAME, value='modal__button--normal')
        normal_mode_button.click()
    except ElementNotInteractableException:
        pass

    # hit 保有商品一覧 button
    a_elements = driver.find_elements(by=By.TAG_NAME, value='a')
    for a_element in a_elements:
        try:
            img_element = a_element.find_element(by=By.TAG_NAME, value='img')
            if "保有商品一覧" == img_element.get_attribute('title'):
                a_element.click()
                break
        except NoSuchElementException:
            pass

    # select 売却 for a specified stock
    table = driver.find_element(by=By.ID, value='poss-tbl-sp')
    tr_elements = table.find_elements(by=By.TAG_NAME, value='tr')
    for tr_element in tr_elements:
        # if "国内債券インデックス" in tr_element.text:
        if "全世界株式" in tr_element.text:
            a_elements = tr_element.find_elements(by=By.TAG_NAME, value='a')
            break
    is_click = False
    for a_element in a_elements:
        try:
            img_elements = a_element.find_elements(by=By.TAG_NAME, value='img')
            for img_element in img_elements:
                print(img_element.get_attribute('alt'))
                if img_element.get_attribute('alt') == '売却':
                    a_element.click()
                    is_click = True
                    break
        except NoSuchElementException:
            pass
        if is_click:
            break

    # select sell all
    # radio_button = driver.find_element(by=By.NAME, value='convCashFlg')
    radio_button = driver.find_element(
        by=By.ID, value='radio-img-cash-cd-all')
    radio_button.click()
    confirm_button = driver.find_element(by=By.ID, value='submitBtn1')
    confirm_button.click()

    sleep(2)

    # hit sell button
    password = driver.find_element(by=By.ID, value='inputTxt_password')
    password.send_keys(second_password)
    # submit_button = driver.find_element(by=By.ID, value='sbm')
    # submit_button.click()

    sleep(120)


def signin_mufg(url, used_id, password):
    # headless mode
    # option = Options()
    # option.add_argument('--headless')
    # driver = webdriver.Chrome(options=option)

    # normal mode
    driver = webdriver.Chrome()

    driver.get(url)
    user_card_no = driver.find_element(by=By.ID, value="tx-contract-number")
    user_card_no.send_keys(used_id)
    user_password = driver.find_element(by=By.ID, value="tx-ib-password")
    user_password.send_keys(password)
    signin_button = driver.find_element(by=By.CLASS_NAME, value="gonext")
    signin_button.click()

    sleep(3)

    driver.execute_script(
        "JavaScript:goAnother('../ibp/toushin/ToushinKouzaShutoku.do'); return false;")

    sleep(3)

    button_sell = driver.find_element(by=By.CLASS_NAME, value='btn-sell')
    button_sell.click()

    sleep(3)

    def hit_tsugihe(driver):
        button_next = driver.find_element(by=By.XPATH,
                                          value="//a[img[@alt='次へ']]")
        button_next.click()

    hit_tsugihe(driver)
    sleep(2)
    hit_tsugihe(driver)
    sleep(3)

    sell_button = driver.find_element(by=By.XPATH,
                                      value="//label[contains(text(), '全部解約')]")
    sell_button.click()
    hit_tsugihe(driver)
    sleep(2)

    button_next = driver.find_element(by=By.XPATH,
                                      value="//a[img[@alt='解約']]")
    button_next.click()
    sleep(300)


def signin_mnx(url, used_id, password, second_password):
    # headless mode
    # option = Options()
    # option.add_argument('--headless')
    # driver = webdriver.Chrome(options=option)

    # normal mode
    driver = webdriver.Chrome()

    driver.get(url)
    user_card_no = driver.find_element(by=By.ID, value="loginid")
    user_card_no.send_keys(used_id)
    user_password = driver.find_element(by=By.ID, value="passwd")
    user_password.send_keys(password)
    signin_button = driver.find_element(by=By.ID,
                                        value="contents")
    signin_button.submit()

    sleep(3)

    mutual_fund_button = driver.find_element(by=By.XPATH,
                                             value='//a[contains(text(), "投信・積立")]')
    mutual_fund_button.click()

    sleep(3)

    sell_button = driver.find_element(by=By.XPATH,
                                      value="//a[contains(text(), '保有残高・売却')]")
    sell_button.click()

    fund_name_flake = '日本債券'
    tr_element = driver.find_element(by=By.XPATH,
                                     value=f'//tr[td[a[strong[contains(text(), "{fund_name_flake}")]]]]')
    a_element = tr_element.find_element(by=By.XPATH,
                                        value='//a[span[contains(text(), "売却")]]')
    a_element.click()

    sleep(3)

    radio_button = driver.find_element(by=By.XPATH,
                                       value='//label[strong[contains(text(), "全部解約")]]')
    radio_button.click()
    radio_button = driver.find_element(by=By.XPATH,
                                       value='//label[contains(text(), "はい")]')
    radio_button.click()

    confirm_button = driver.find_element(by=By.XPATH,
                                         value="//input[@value='次へ（注文内容確認）']")
    confirm_button.click()
    sleep(3)

    second_password_element = driver.find_element(by=By.ID, value='idPinNo')
    second_password_element.send_keys(second_password)

    sleep(120)

    # confirm_button = driver.find_element(by=By.XPATH,
    #                                      value="//input[@value='実行する']")
    # confirm_button.click()


if __name__ == "__main__":
    configs = read_config()
    signin_sb(configs['sbi']['url'],
              configs['sbi']['user_id'],
              configs['sbi']['password'],
              configs['sbi']['second_password'])
    # signin_rs(configs['rakuten']['url'], configs['rakuten']['user_id'], configs['rakuten']['password'],
    #           configs['rakuten']['second_password'])
    # signin_mufg(configs['mufg']['url'], configs['mufg']
    #             ['user_id'], configs['mufg']['password'])
    # signin_mnx(configs['monex']['url'],
    #            configs['monex']['user_id'],
    #            configs['monex']['password'],
    #            configs['monex']['second_password'])
    pass
