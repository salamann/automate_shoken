from datetime import datetime
import yaml
from time import sleep
import smtplib
from email.mime.text import MIMEText

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotInteractableException,
    UnexpectedAlertPresentException,
)
import pandas
from webdriver_manager.chrome import ChromeDriverManager


def send_email(
    to_email,
    subject,
    message,
    smtp_server,
    smtp_port_number,
    smtp_user_name,
    smtp_password,
    from_email,
) -> None:
    msg = MIMEText(message, "html", "utf-8")
    msg["Subject"] = subject
    msg["To"] = to_email
    msg["From"] = from_email

    server = smtplib.SMTP(smtp_server, smtp_port_number)
    server.starttls()
    server.login(smtp_user_name, smtp_password)
    server.send_message(msg)

    server.quit()


def webdriver_start(mode="h") -> WebDriver:
    # headless mode
    if mode == "h":
        options = Options()
        # options.binary_location = '/usr/bin/google-chrome'
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--lang=ja-JP")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36"
        )

        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )

    # normal mode
    if mode == "n":
        options = Options()
        # options.add_argument('--no-sandbox')
        # options.add_argument('--headless')
        # options.add_argument('--disable-gpu')
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        )

        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )

    # chrome beta mode
    if mode == "b":
        options = Options()
        configs = read_config(file_name="driver_settings.yaml")
        options.binary_location = configs["chrome"]["path"]
        chrome_service = Service(executable_path=configs["chrome"]["driver_path"])

        return webdriver.Chrome(service=chrome_service, options=options)


def read_config(file_name="config.yaml"):
    with open(file_name, "r", encoding="utf-8") as f:
        configs = yaml.safe_load(f)
    return configs


def signin_sb(url, user_id, password, second_password, fund_name):
    driver = webdriver_start()

    driver.get(url)
    driver.maximize_window()
    user_card_no = driver.find_element(by=By.NAME, value="user_id")
    user_card_no.send_keys(user_id)
    user_password = driver.find_element(by=By.NAME, value="user_password")
    user_password.send_keys(password)
    signin_button = driver.find_element(by=By.NAME, value="ACT_login")
    signin_button.click()

    sleep(3)
    a_element = driver.find_element(
        by=By.XPATH, value="//a[img[@title='ポートフォリオ']]"
    )
    a_element.click()

    try:
        table_element = driver.find_element(
            by=By.XPATH,
            value=f'//table[tbody[tr[td[a[contains(text(), "{fund_name}")]]]]]',
        )
        [df_fund] = pandas.read_html(table_element.get_attribute("outerHTML"))
        df_fund.columns = df_fund.loc[0, :].to_list()
        df_fund = df_fund.loc[1:, :]
        index = df_fund["ファンド名"].str.contains(fund_name).to_list().index(True)
        a_element = table_element.find_elements(
            by=By.XPATH, value='//a[font[contains(text(), "売却")]]'
        )[index]
        a_element.click()

        # fill the blanks and hit the sell button
        radio_button = driver.find_element(by=By.ID, value="buy_sell_202")
        radio_button.click()
        password_field = driver.find_element(by=By.ID, value="pwd3")
        password_field.send_keys(second_password)
        check_box = driver.find_element(by=By.NAME, value="skip_estimate")
        check_box.click()
        radio_button = driver.find_element(by=By.NAME, value="ACT_place")
        radio_button.click()
        sleep(1)
        return True
    except NoSuchElementException:
        return False


def signin_rs(url, user_id, password, second_password, fund_name):
    driver = webdriver_start(mode="n")

    driver.get(url)
    driver.maximize_window()
    user_card_no = driver.find_element(by=By.ID, value="form-login-id")
    user_card_no.send_keys(user_id)
    user_password = driver.find_element(by=By.ID, value="form-login-pass")
    user_password.send_keys(password)
    signin_button = driver.find_element(by=By.ID, value="login-btn")
    signin_button.click()

    sleep(3)

    # hit 投資信託 button
    a_element = driver.find_element(
        by=By.XPATH, value='//a[span[contains(text(), "投資信託")]]'
    )
    a_element.click()

    # hit normal mode if it happens
    try:
        normal_mode_button = driver.find_element(
            by=By.CLASS_NAME, value="modal__button--normal"
        )
        normal_mode_button.click()
    except (ElementNotInteractableException, NoSuchElementException):
        pass
    sleep(3)
    # hit 保有商品一覧 button
    driver.find_element(
        By.XPATH, '//button[span[contains(text(), "保有商品")]]'
    ).click()

    # select 売却 for a specified stock
    # try:
    try:
        table_element = driver.find_element(
            by=By.XPATH,
            value=f'//table[tbody[tr[td[div[a[contains(text(), "{fund_name}")]]]]]]',
        )
        df_fund = pandas.read_html(table_element.get_attribute("outerHTML"))[0]
        df_fund = df_fund[~df_fund["あし あと"].isnull()]
        index = df_fund["ファンド"].str.contains(fund_name).to_list().index(True)
        a_element = table_element.find_elements(
            by=By.XPATH, value='//a[img[@alt="売却"]]'
        )[index]
        driver.execute_script("arguments[0].click();", a_element)
        # a_element.click()

        # select sell all
        radio_button = driver.find_element(
            by=By.XPATH,
            value='//label[span[span[span[span[contains(text(), "全部売却")]]]]]',
        )
        radio_button.click()
        confirm_button = driver.find_element(by=By.ID, value="submitBtn1")
        confirm_button.click()

        sleep(2)

        # hit sell button
        password = driver.find_element(by=By.ID, value="inputTxt_password")
        password.send_keys(second_password)
        submit_button = driver.find_element(by=By.ID, value="sbm")
        submit_button.click()

        sleep(1)
        return True
    except NoSuchElementException:
        return False


def signin_mufg(url, user_id, password, fund_name):
    driver = webdriver_start()

    driver.get(url)
    driver.maximize_window()
    user_card_no = driver.find_element(by=By.ID, value="tx-contract-number")
    user_card_no.send_keys(user_id)
    user_password = driver.find_element(by=By.ID, value="tx-ib-password")
    user_password.send_keys(password)
    signin_button = driver.find_element(by=By.CLASS_NAME, value="gonext")
    signin_button.click()

    sleep(3)

    driver.execute_script(
        "JavaScript:goAnother('../ibp/toushin/ToushinKouzaShutoku.do'); return false;"
    )

    sleep(3)

    button_sell = driver.find_element(by=By.CLASS_NAME, value="btn-sell")
    button_sell.click()

    sleep(3)

    try:

        def hit_tsugihe(driver):
            button_next = driver.find_element(
                by=By.XPATH, value="//a[img[@alt='次へ']]"
            )
            button_next.click()

        hit_tsugihe(driver)
        sleep(2)
        hit_tsugihe(driver)
        sleep(3)

        sell_button = driver.find_element(
            by=By.XPATH, value="//label[contains(text(), '全部解約')]"
        )
        sell_button.click()
        hit_tsugihe(driver)
        sleep(2)

        button_next = driver.find_element(by=By.XPATH, value="//a[img[@alt='解約']]")
        button_next.click()
        sleep(1)
        return True
    except UnexpectedAlertPresentException:
        return False


def signin_mnx(url, user_id, password):
    driver = webdriver_start()

    driver.get(url)
    driver.maximize_window()
    user_card_no = driver.find_element(by=By.ID, value="loginid")
    user_card_no.send_keys(user_id)
    user_password = driver.find_element(by=By.ID, value="passwd")
    user_password.send_keys(password)
    user_password.submit()
    # signin_button = driver.find_element(by=By.ID,
    #                                     value="contents")
    # signin_button.submit()

    sleep(3)
    return driver


def move_point_mnx(url, user_id, password):
    driver: WebDriver = signin_mnx(url, user_id, password)
    driver.maximize_window()
    driver.find_element(By.XPATH, '//a[text()="マネックスポイント"]').click()
    sleep(3)
    driver.find_element(By.XPATH, '//a[img[@alt="Pontaポイント"]]').click()
    sleep(3)

    driver.find_element(By.XPATH, '//a[text()="交換"]').click()
    sleep(3)
    try:
        table = driver.find_elements(by=By.TAG_NAME, value="table")[1]
        [df_fund] = pandas.read_html(table.get_attribute("outerHTML"))
        ponta_point_num = int(df_fund.loc[0, df_fund.columns[-1]].replace("個", ""))

        driver.find_element(By.XPATH, '//input[@name="orderQuantity"]').send_keys(
            ponta_point_num
        )
        driver.find_element(By.XPATH, '//input[@alt="次へ（入力内容確認）"]').click()
        sleep(3)
        driver.find_element(By.XPATH, '//input[@alt="ポイントを使う"]').click()
        sleep(3)
        return True
    except IndexError:
        return False


def move_money_mnx(url, user_id, password, second_password):
    driver: WebDriver = signin_mnx(url, user_id, password)
    driver.maximize_window()

    mutual_fund_button = driver.find_element(
        by=By.XPATH, value='//a[contains(text(), "入出金")]'
    )
    mutual_fund_button.click()
    sleep(3)
    mutual_fund_button = driver.find_element(
        by=By.XPATH, value='//a[text()="出金指示"]'
    )
    driver.get(mutual_fund_button.get_attribute("href"))

    table = driver.find_elements(by=By.TAG_NAME, value="table")[-1]
    [df_fund] = pandas.read_html(table.get_attribute("outerHTML"))
    max_amount = df_fund[df_fund[0].str.contains("出金可能額")].loc[:, 1].to_list()[0]
    max_amount = max_amount.replace("円", "").replace(",", "")
    if int(max_amount) != 0:
        input_amount = driver.find_element(by=By.ID, value="Amount")
        input_amount.send_keys(max_amount)
        input_amount.submit()
        sleep(3)

        input_amount = driver.find_element(by=By.ID, value="idPinNo")
        input_amount.send_keys(second_password)
        input_amount.submit()
        sleep(3)
        driver.close()
        return True
    else:
        driver.close()
        return False


def sell_mnx(url, user_id, password, second_password, fund_name):
    driver: WebDriver = signin_mnx(url, user_id, password)
    driver.maximize_window()

    mutual_fund_button = driver.find_element(
        by=By.XPATH, value='//a[contains(text(), "投信･積立")]'
    )
    mutual_fund_button.click()

    sleep(3)

    sell_button = driver.find_elements(
        by=By.XPATH, value="//a[contains(text(), '保有残高・売却')]"
    )[-1]
    driver.get(sell_button.get_attribute("href"))
    # sell_button.click()

    try:
        table_element = driver.find_element(
            by=By.XPATH,
            value=f'//table[tbody[tr[td[a[strong[contains(text(), "{fund_name}")]]]]]]',
        )
        [df_fund] = pandas.read_html(table_element.get_attribute("outerHTML"))
        index = df_fund["銘柄"].str.contains(fund_name).to_list().index(True)
        a_element = table_element.find_elements(
            by=By.XPATH, value='//a[span[contains(text(), "売却")]]'
        )[index]
        a_element.click()

        sleep(3)

        radio_button = driver.find_element(
            by=By.XPATH, value='//label[strong[contains(text(), "全部解約")]]'
        )
        radio_button.click()
        radio_button = driver.find_element(
            by=By.XPATH, value='//label[contains(text(), "はい")]'
        )
        radio_button.click()

        confirm_button = driver.find_element(
            by=By.XPATH, value="//input[@value='次へ（注文内容確認）']"
        )
        confirm_button.click()
        sleep(3)

        second_password_element = driver.find_element(by=By.ID, value="idPinNo")
        second_password_element.send_keys(second_password)

        sleep(3)

        confirm_button = driver.find_element(
            by=By.XPATH, value="//input[@value='実行する']"
        )
        confirm_button.click()
        return True
    except NoSuchElementException:
        return False


def buy_nikko(url, user_id, password, second_password, fund_name):
    try:
        driver = webdriver_start()
        driver.get(url)
        driver.maximize_window()
        sleep(10)
        driver.find_element(by=By.NAME, value="branch-code").send_keys(user_id)

        password_box = driver.find_element(by=By.NAME, value="password")
        password_box.send_keys(password)
        password_box.submit()
        sleep(10)

        driver.get(f"https://froggy.smbcnikko.co.jp/stock/{fund_name}")
        sleep(10)

        button = driver.find_element(
            by=By.XPATH, value='//button[contains(text(), "買う")]'
        )
        button.click()
        sleep(10)

        driver.find_element(by=By.XPATH, value='//input[@type="tel"]').send_keys(200)
        try:
            driver.find_element(by=By.CLASS_NAME, value="orderForm__checkbox").click()
        except NoSuchElementException:
            pass
        button = driver.find_element(
            by=By.XPATH, value='//button[contains(text(), "注文内容を確認する")]'
        )
        button.click()

        sleep(10)
        driver.find_element(by=By.XPATH, value='//input[@type="password"]').send_keys(
            second_password
        )

        button = driver.find_element(
            by=By.XPATH, value='//button[contains(text(), "この内容で注文する")]'
        )
        button.click()
        sleep(10)

        return True
    except Exception as e:
        return str(e)


def wrapper(payload: dict) -> bool:
    func: callable = globals()[payload["func_name"]]
    try:
        if ("second_password" in payload) & ("fund_name" in payload):
            response = func(
                payload["url"],
                payload["user_id"],
                payload["password"],
                payload["second_password"],
                payload["fund_name"],
            )
        elif ("second_password" not in payload) & ("fund_name" in payload):
            response = func(
                payload["url"],
                payload["user_id"],
                payload["password"],
                payload["fund_name"],
            )
        elif ("second_password" in payload) & ("fund_name" not in payload):
            response = func(
                payload["url"],
                payload["user_id"],
                payload["password"],
                payload["second_password"],
            )
        elif ("second_password" not in payload) & ("fund_name" not in payload):
            response = func(payload["url"], payload["user_id"], payload["password"])

    except Exception as e:
        response = str(e)
    return response


if __name__ == "__main__":
    configs = read_config()

    responses = {}
    text = f"{str(datetime.today().date())}"
    for key, value in configs.items():
        responses[key] = wrapper(value)
        text += f",{responses[key]}"

    with open("log.csv", "a", encoding="utf-8") as f:
        f.write(text)

    from config import from_email, to_email
    from config import smtp_server, smtp_port_number, smtp_user_name, smtp_password

    send_email(
        to_email,
        "Fund Status",
        str(responses),
        smtp_server,
        smtp_port_number,
        smtp_user_name,
        smtp_password,
        from_email,
    )
