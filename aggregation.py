
import yaml
from time import sleep
import json

# from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
import pandas
import requests

from cruise import webdriver_start

with open('mappings.json', 'r', encoding='utf-8') as f:
    mappings = json.load(f)


def transpose(_list: list) -> list:
    return list(zip(*_list))


def remove_yen_and_comma(text: str) -> str:
    return float(text.replace(',', '').replace('円', '').strip())


def remove_comma_from_list(_list: iter) -> list:
    return [int(_elem.replace(',', '')) for _elem in _list]


def signin_rs_stock(user_id, password):
    url = 'https://www.rakuten-sec.co.jp/'
    driver = webdriver_start()

    driver.get(url)
    print(driver.title)
    user_card_no = driver.find_element(by=By.ID, value="form-login-id")
    user_card_no.send_keys(user_id)
    user_password = driver.find_element(by=By.ID, value="form-login-pass")
    user_password.send_keys(password)
    signin_button = driver.find_element(by=By.ID, value="login-btn")
    signin_button.click()

    sleep(3)

    # hit 投資信託 button
    a_element = driver.find_element(by=By.XPATH,
                                    value='//a[span[contains(text(), "国内株式")]]')
    a_element.click()

    # hit normal mode if it happens
    try:
        normal_mode_button = driver.find_element(
            by=By.CLASS_NAME, value='modal__button--normal')
        normal_mode_button.click()
    except NoSuchElementException:
        pass

    # hit 保有商品一覧 button
    a_element = driver.find_element(by=By.XPATH,
                                    value='//a[img[@title="保有銘柄一覧"]]')
    a_element.click()

    # select 売却 for a specified stock
    table_element = driver.find_element(by=By.XPATH,
                                        value='//table[@id="poss-tbl-sp"]')

    df = pandas.read_html(table_element.get_attribute('outerHTML'))[0]
    df.columns = df.loc[0, :]
    df = df.loc[list(range(len(df)))[1::3], :]
    columns = [_ for _ in df.columns.to_list() if _ == _]
    amount_name = [col for col in columns if '保有数量' in col][0]
    current_value_name = [
        col for col in columns if '現在値' in col][0]
    base_value_name = [col for col in columns
                       if '平均取得価' in col][0]
    df['amount'] = [int(_amount.replace('株', '').replace(',', ''))
                    for _amount in df[amount_name]]
    df['base_price'] = [float(_amount.split('円')[0].replace(',', ''))
                        for _amount in df[base_value_name]]
    df['current_price'] = [float(_amount.split('円')[0].strip().replace(',', ''))
                           for _amount in df[current_value_name]]
    df['fund_code'] = [mappings[name] for name in df['銘柄']]
    df['retrieved_by'] = ['rakuten'] * len(df)

    return df[['fund_code', 'current_price', 'base_price', 'amount', 'retrieved_by']].to_dict(orient='records')


def signin_rs_nisa(user_id, password):
    url = 'https://www.rakuten-sec.co.jp/'
    driver = webdriver_start()

    driver.get(url)
    print(driver.title)
    user_card_no = driver.find_element(by=By.ID, value="form-login-id")
    user_card_no.send_keys(user_id)
    user_password = driver.find_element(by=By.ID, value="form-login-pass")
    user_password.send_keys(password)
    signin_button = driver.find_element(by=By.ID, value="login-btn")
    signin_button.click()

    sleep(3)

    # hit ジュニアNISA button
    a_element = driver.find_element(by=By.XPATH,
                                    value='//a[@class="pcm-gl-nisa-switch__link" and contains(text(), "ジュニア")]')
    a_element.click()

    # hit 保有資産の状況を確認するボタン
    try:
        driver.find_element(by=By.XPATH,
                            value='//a[img[@alt="保有資産の状況を確認する"]]').click()
    except:
        driver.find_element(by=By.XPATH,
                            value='//div[img[@src="/member/images/btn-close-gray.png"]]').click()
        sleep(2)
        driver.find_element(by=By.XPATH,
                            value='//a[img[@alt="保有資産の状況を確認する"]]').click()

    sleep(3)

    # hit 投資信託ボタン
    driver.find_element(by=By.XPATH,
                        value='//li[contains(@class, "last-child  ass-tab")]').click()
    sleep(3)

    # get table
    table = driver.find_element(by=By.XPATH,
                                value='//table[@id="poss-tbl-nisa"]')

    df = pandas.read_html(table.get_attribute('outerHTML'))[0]
    df = df.loc[list(range(len(df)))[::3][:-1], :]
    amount_name = [col for col in df.columns.to_list() if '保有数量' in col][0]
    current_value_name = [
        col for col in df.columns.to_list() if '基準価額' in col][0]
    base_value_name = [col for col in df.columns.to_list()
                       if '平均取得価' in col][0]
    df['amount'] = [int(_amount.replace('口', '').replace(',', ''))
                    for _amount in df[amount_name]]
    df['base_price'] = [float(_amount.split('円')[0].replace(',', ''))
                        for _amount in df[base_value_name]]
    df['current_price'] = [int(_amount.split('円')[0].strip().replace(',', ''))
                           for _amount in df[current_value_name]]
    df['fund_code'] = [mappings[name] for name in df['ファンド']]
    df['retrieved_by'] = ['rakuten_jr_nisa'] * len(df)

    return df[['fund_code', 'current_price', 'base_price', 'amount', 'retrieved_by']].to_dict(orient='records')


def signin_rs(user_id, password):
    url = 'https://www.rakuten-sec.co.jp/'
    driver = webdriver_start()

    driver.get(url)
    print(driver.title)
    user_card_no = driver.find_element(by=By.ID, value="form-login-id")
    user_card_no.send_keys(user_id)
    user_password = driver.find_element(by=By.ID, value="form-login-pass")
    user_password.send_keys(password)
    signin_button = driver.find_element(by=By.ID, value="login-btn")
    signin_button.click()

    sleep(3)

    # hit 投資信託 button
    a_element = driver.find_element(by=By.XPATH,
                                    value='//a[span[contains(text(), "投資信託")]]')
    a_element.click()

    # hit normal mode if it happens
    try:
        normal_mode_button = driver.find_element(
            by=By.CLASS_NAME, value='modal__button--normal')
        normal_mode_button.click()
    except ElementNotInteractableException:
        pass

    # hit 保有商品一覧 button
    a_element = driver.find_element(by=By.XPATH,
                                    value='//a[img[@title="保有商品一覧"]]')
    a_element.click()

    # select 売却 for a specified stock
    table_element = driver.find_element(by=By.XPATH,
                                        value='//table[@id="poss-tbl-sp"]')

    df = pandas.read_html(table_element.get_attribute('outerHTML'))[0]
    df = df.loc[list(range(len(df)))[::3][:-1], :]
    amount_name = [col for col in df.columns.to_list() if '保有数量' in col][0]
    current_value_name = [
        col for col in df.columns.to_list() if '基準価額' in col][0]
    base_value_name = [col for col in df.columns.to_list()
                       if '平均取得価' in col][0]
    df['amount'] = [int(_amount.replace('口', '').replace(',', ''))
                    for _amount in df[amount_name]]
    df['base_price'] = [float(_amount.split('円')[0].replace(',', ''))
                        for _amount in df[base_value_name]]
    df['current_price'] = [int(_amount.split('円')[0].strip().replace(',', ''))
                           for _amount in df[current_value_name]]
    df['fund_code'] = [mappings[name] for name in df['ファンド']]
    df['retrieved_by'] = ['rakuten'] * len(df)

    return df[['fund_code', 'current_price', 'base_price', 'amount', 'retrieved_by']].to_dict(orient='records')


def nrk(user_name, password):
    url = "https://www.nrkn.co.jp/rk/login.html"
    driver = webdriver_start()

    driver.get(url)
    print(driver.title)
    sleep(3)
    driver.find_element(by=By.NAME, value='userId').send_keys(user_name)
    driver.find_element(by=By.NAME, value='password').send_keys(password)
    driver.find_element(by=By.ID, value='btnLogin').click()
    sleep(3)
    driver.find_element(by=By.ID, value='mainMenu01').find_element(
        by=By.TAG_NAME, value='a').click()
    sleep(3)
    div_elements = driver.find_elements(
        by=By.XPATH, value='//div[@class="infoDetailUnit_02 pc_mb30"]')
    res = []
    for div_element in div_elements:
        fund_name = div_element.find_element(by=By.TAG_NAME, value='dd').text
        table = div_element.find_element(by=By.TAG_NAME, value='table')
        df = pandas.read_html(table.get_attribute('outerHTML'))[0]
        amount = df.loc[0, '数量（残高）']
        datum = {}
        datum['fund_code'] = mappings[fund_name]
        datum['amount'] = amount
        datum['current_price'] = remove_yen_and_comma(df.loc[0, '基準価額'])
        datum['base_price'] = remove_yen_and_comma(
            df.loc[0, '取得価額累計']) / amount * 10000
        datum['retrieved_by'] = 'nrk'
        res.append(datum)
    driver.find_element(
        by=By.XPATH, value='//a[contains(text(), "ログアウト")]').click()
    return res


def kabucom_signin(user_name, password):
    url = 'https://s10.kabu.co.jp/_mem_bin/members/login.asp?/members/'
    driver = webdriver_start()

    driver.get(url)
    print(driver.title)
    sleep(5)

    driver.find_element(by=By.NAME, value='SsLogonUser').send_keys(user_name)
    password_cell = driver.find_element(by=By.NAME, value='SsLogonPassword')
    password_cell.send_keys(password)
    password_cell.submit()

    sleep(5)
    return driver


def kabucom_nisa(user_name, password):
    nisa_url = 'https://s20.si0.kabu.co.jp/members/account/accountstatusNISA/AccountStatusToshin.asp'
    return kabucom_fund(nisa_url, user_name, password)


def kabucom_general_fund(user_name, password):
    fund_url = 'https://s20.si0.kabu.co.jp/members/account/accountstatus/AccountStatusToshin.asp'

    return kabucom_fund(fund_url, user_name, password)


def kabucom_stock(user_name, password):
    driver = kabucom_signin(user_name, password)

    stock_url = "https://s20.si0.kabu.co.jp/ap/pc/Stocks/Stock/Position/List"

    driver.get(stock_url)
    print(driver.title)
    table = driver.find_element(
        by=By.XPATH, value=('//table[tbody[tr[td[contains(text(), "明")]]]]'))
    return kabucom_table_to_df_stock(table)


def kabucom_fund(url, user_name, password):
    driver = kabucom_signin(user_name, password)

    driver.get(url)
    print(driver.title)
    table = driver.find_element(
        by=By.XPATH, value='//table[@class="table_status"]')
    return kabucom_table_to_df(table)


def kabucom_table_to_df_stock(table):
    df = pandas.read_html(table.get_attribute('outerHTML'))[0]
    df.columns = df.loc[0, :]
    df = df.loc[1:, :].set_index('銘柄(コード) 本決算/中間決算')
    amount = [_value.replace('口', '')
              for _value in df.loc[:, '保有株数 (注文中等)'].to_list()]
    current_price, base_price, _ = transpose([_value.split('円')
                                              for _value in df.loc[:, '現在値  平均取得単価'].to_list()])

    current_price = remove_comma_from_list(current_price)
    amount = remove_comma_from_list(amount)
    base_price = remove_comma_from_list(base_price)

    df['fund_code'] = [mappings[key] for key in df.index]
    df['current_price'] = current_price
    df['base_price'] = base_price
    df['amount'] = amount
    df['retrieved_by'] = ['kabucom'] * len(amount)

    return df[['fund_code', 'current_price', 'base_price', 'amount', 'retrieved_by']].to_dict(orient='records')


def kabucom_table_to_df(table):
    df = pandas.read_html(table.get_attribute('outerHTML'))[0]
    df.columns = df.loc[0, :]
    df = df.loc[1:, :]
    df = df.set_index('ファンド名')
    current_price, amount = transpose([_value.replace('口', '').split('円')
                                       for _value in df.loc[:, '基準価額 口数(注文中)'].to_list()])
    if '個別元本 買付単価' in df.columns:
        _, base_price, _ = transpose([_value.replace('口', '').split('円')
                                      for _value in df.loc[:, '個別元本 買付単価'].to_list()])
    elif '個別元本 取得単価' in df.columns:
        _, base_price, _ = transpose([_value.replace('口', '').split('円')
                                      for _value in df.loc[:, '個別元本 取得単価'].to_list()])

    current_price = remove_comma_from_list(current_price)
    amount = remove_comma_from_list(amount)
    base_price = remove_comma_from_list(base_price)

    df['fund_code'] = [mappings[key] for key in df.index]
    df['current_price'] = current_price
    df['base_price'] = base_price
    df['amount'] = amount
    df['retrieved_by'] = ['kabucom'] * len(amount)

    return df[['fund_code', 'current_price', 'base_price', 'amount', 'retrieved_by']].to_dict(orient='records')


def matsui(user_name, password):
    url = 'https://www.deal.matsui.co.jp/ITS/login/MemberLogin.jsp'
    driver = webdriver_start()
    driver.get(url)
    print(driver.title)
    sleep(5)
    driver.find_element(by=By.NAME, value='clientCD').send_keys(user_name)
    driver.find_element(by=By.NAME, value='passwd').send_keys(password)
    driver.find_element(by=By.ID, value='btn_opn_login').click()
    sleep(3)
    target_frame = driver.find_element(by=By.NAME, value="GM")
    driver.switch_to.frame(target_frame)

    for global_menu in driver.find_elements(by=By.CLASS_NAME, value="globalmenu"):
        if "株式取引" in str(global_menu.text):
            global_menu.click()
            break

    target_frame = driver.find_element(by=By.NAME, value="LM")
    driver.switch_to.frame(target_frame)

    for link in driver.find_elements(by=By.TAG_NAME, value="a"):
        if "現物売" in str(link.text):
            link.click()
            break

    target_frame = driver.find_element(by=By.NAME, value="CT")
    driver.switch_to.frame(target_frame)

    table = driver.find_element(by=By.XPATH,
                                value='//table[tbody[tr[td[font[contains(text(), "注文")]]]]]')
    df = pandas.read_html(table.get_attribute('outerHTML'))[0]
    df.columns = df.loc[0, :]
    df = df.loc[1:, :]
    df["amount"] = df['保有数 [株]']
    df["fund_code"] = [mappings[name] for name in df['銘柄'].to_list()]
    df['base_price'] = df['平均取得単価 [円]']
    df['current_price'] = [remove_yen_and_comma(
        elem.split()[0]) for elem in df['評価単価[円] 前日比[円]'].to_list()]
    df['retrieved_by'] = ['matsui'] * len(df['current_price'])
    return df[['fund_code', 'current_price', 'base_price', 'amount', 'retrieved_by']].to_dict(orient='records')


def get_mochikabu(user_name, password, fund_code):
    url = "https://www.e-plan.nomura.co.jp/login/index.html"
    driver = webdriver_start()
    driver.get(url)
    sleep(5)
    print(driver.title)

    driver.find_element(by=By.ID,
                        value='m_login_mail_address').send_keys(user_name)
    password_cell = driver.find_element(by=By.ID,
                                        value='m_login_mail_password')
    password_cell.send_keys(password)
    password_cell.submit()

    sleep(10)
    values = driver.find_elements(by=By.XPATH,
                                  value='//span[@class="m_home_mydate_result_score"]')

    for _index, _element in enumerate(values):
        if _index == 0:
            amount = remove_yen_and_comma(_element.text)
        elif _index == 1:
            current_price = remove_yen_and_comma(_element.text) / amount
        elif _index == 2:
            base_price = remove_yen_and_comma(_element.text) / amount
    df = {'fund_code': fund_code,
          'amount': amount,
          'current_price': current_price,
          'base_price': base_price,
          'retrieved_by': 'mochikabu'}
    return [df]

def get_usdjpy():
    smbc = pandas.read_html(requests.get('https://www.smbc.co.jp/ex/ExchangeServlet?ScreenID=real').content)
    return sum(smbc[0].loc[0, :].to_list()[1:])/2

def run_all_with_configs(configs):
    data = []
    for name, values in configs.items():
        if name == "mochikabu":
            data += get_mochikabu(values['user_name'],
                                  values['password'],
                                  values['fund_code'])
        if name == "kabucom":
            data += kabucom_nisa(values['user_name'],
                                 values['password'])
            data += kabucom_general_fund(values['user_name'],
                                         values['password'])
            data += kabucom_stock(values['user_name'],
                                  values['password'])
        if name == 'rakuten':
            data += signin_rs(values['user_name'],
                              values['password'])
            data += signin_rs_stock(values['user_name'],
                                    values['password'])
        if name == 'rakuten_nisa':
            data += signin_rs_nisa(values['user_name'],
                                   values['password'])
        if name == 'nrk':
            data += nrk(values['user_name'],
                        values['password'])
        if name == 'matsui':
            data += matsui(values['user_name'],
                           values['password'])
    return data


def read_configs(file_name='accounts.yaml'):
    with open(file_name, 'r', encoding='utf-8') as f:
        configs = yaml.safe_load(f)
    return configs


def sum_funds(df: pandas.DataFrame):
    unique_stocks = sorted(list(set(df['fund_code'].to_list())))
    stocks = []
    for stock_name in unique_stocks:
        res = {}
        total_value = 0
        total_amount = 0
        for code, base, amount, current in zip(df['fund_code'], df['base_price'], df['amount'], df['current_price']):
            if code == stock_name:
                total_value += int(base) * int(amount)
                total_amount += int(amount)
                current_price = int(current)
        res['fund_code'] = str(stock_name)
        res['amount'] = total_amount
        res['average_price'] = total_value / total_amount
        res['current_price'] = current_price
        res['total_value'] = total_amount * current_price
        res['total_cost'] = total_amount * res['average_price']

        if len(stock_name) > 5:
            res['total_value'] /= 10000
            res['total_cost'] /= 10000
        res['total_value'], res['total_cost'] = int(
            res['total_value']), int(res['total_cost'])
        res['profitloss'] = res['total_value'] - res['total_cost']
        with open("mappings_names.yaml", "r", encoding='utf-8') as f:
            names = yaml.safe_load(f)
        res['fund_name'] = names[res['fund_code']]
        stocks.append(res)
    return stocks

def schwab(user_name, password):
 
    url = 'https://www.schwab.com/client-home'
    # url = 'https://client.schwab.com/Login/SignOn/CustomerCenterLogin.aspx'
    driver = webdriver_start(mode='n')
    driver.maximize_window()
    driver.get(url)
    sleep(5)
    print(driver.title)
    
    driver.switch_to.frame('schwablmslogin')
    # driver.switch_to.frame('lmsSecondaryLogin')
    driver.find_element(By.ID, 'loginIdInput').send_keys(user_name)
    sleep(1)
    driver.find_element(By.ID, 'passwordInput').send_keys(password)
    sleep(1)
    driver.find_element(By.ID, 'btnLogin').click()

    sleep(5)

    driver.get('https://client.schwab.com/Areas/Accounts/Positions')
    sleep(5)
    html = driver.find_element(By.TAG_NAME, 'html')
    [df] = pandas.read_html(html.get_attribute('outerHTML'))
    

    usdjpy = get_usdjpy()

    df.columns = [_col.split(',')[0] for _col in df.columns]
    indices = [_index for _index, _quantity in enumerate(df['Quantity']) if isinstance(_quantity, str)][1:-1]
    df = df.loc[indices, :]
    df = df.loc[:, ['Symbol', 'Quantity', 'Price', 'Cost/Share']]
    df.columns = ['fund_code', 'amount', 'current_price', 'base_price']
    df['retrieved_by'] = ['schwab'] * len(df)
    df['amount'] = df['amount'].astype(float)
    df['current_price'] = [float(_cp.replace('$', ''))*usdjpy for _cp in df['current_price']]
    df['base_price'] = [float(_cp.replace('$', ''))*usdjpy for _cp in df['base_price']]
    return df.to_dict(orient='records')

if __name__ == "__main__":
    # # df = pandas.DataFrame(run_all())
    df = pandas.DataFrame(run_all_with_configs(read_configs()))
    df.to_pickle('portfolio.zip')
    elements = sum_funds(pandas.read_pickle('portfolio.zip'))
    from spreadsheet import update_spreadsheet
    res = update_spreadsheet(elements)
    print(res)
    df = pandas.DataFrame(elements)
    pass
