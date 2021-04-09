from selenium import webdriver
import time
from openpyxl import Workbook
import datetime
from selenium.webdriver.common.keys import Keys
import pyperclip
import pandas as pd


# 검색할 물건
thing = '맥북 m1'

# 다음페이지 몇 번 할지
next = 3

# 총 몇 페이지
total_page = 35
total_next = total_page // 10
last_page = total_page % 10

# datetime
now = datetime.datetime.now()
today = now.strftime('%Y-%m-%d')

# 엑셀
wb = Workbook(write_only=True)
ws = wb.create_sheet(today)
ws.append(['작성날짜', '판매 상태', '제목', 'url', '가격'])

# 중고나라 들어가기
driver = webdriver.Chrome()
driver.implicitly_wait(3)
driver.get('https://cafe.naver.com/joonggonara')
driver.maximize_window()
time.sleep(1)

# 로그인 버튼을 찾고 클릭합니다.
login_btn = driver.find_element_by_css_selector('#gnb_login_button')
login_btn.click()
time.sleep(1)

# id, pw 입력할 곳을 찾습니다.
tag_id = driver.find_element_by_name('id')
tag_pw = driver.find_element_by_name('pw')
tag_id.clear()
time.sleep(1)

# id 입력
tag_id.click()
pyperclip.copy('####')
tag_id.send_keys(Keys.CONTROL, 'v')
time.sleep(1)

# pw 입력
tag_pw.click()
pyperclip.copy('####')
tag_pw.send_keys(Keys.CONTROL, 'v')
time.sleep(1)

# 로그인 버튼을 클릭합니다
login_btn = driver.find_element_by_id('log.login')
login_btn.click()

# 검색
driver.find_element_by_css_selector('#topLayerQueryInput').send_keys(thing)
driver.find_element_by_css_selector('#cafe-search .btn').click()
time.sleep(1)

# iframe 들어가기
driver.switch_to.frame('cafe_main')

# 제목만으로 바꾸기
driver.find_element_by_css_selector('#currentSearchByTop').click()
time.sleep(1)
driver.find_elements_by_css_selector('#sl_general li')[1].click()
time.sleep(1)
driver.find_element_by_css_selector('.btn-search-green').click()
time.sleep(1)

for _ in range(next):
    for page in range(10):
        for i in range(len(driver.find_elements_by_css_selector('.article'))):

            # 게시글 들어가기
            articles = driver.find_elements_by_css_selector('a.article')[i]
            articles.click()
            time.sleep(1)

            # 정보추출
            write_date = driver.find_element_by_css_selector('.date').text
            product_title = driver.find_element_by_css_selector('h3.title_text').text
            url = driver.find_element_by_css_selector('.button_url').get_attribute('href')
            # 가격을 못찾으면 그냥 빈칸 입력
            try:
                # 가격 문자열을 숫자로 바꾸기
                product_price_str = driver.find_element_by_css_selector('.ProductPrice').text
                price_no_won = product_price_str[:-1]
                price_no_won_shim = price_no_won.replace(',', '')
                product_price = int(price_no_won_shim)
            except:
                # 제목에서 가격 문자열 추출
                try:
                    product_title = product_title.replace('[', '')
                    product_title = product_title.replace(']', '&')
                    product_price_str = product_title.split('&')[-2]

                    # 가격 문자열을 숫자로 바꾸기
                    price_no_won = product_price_str[:-1]
                    price_no_won_shim = price_no_won.replace(',', '')
                    product_price = int(price_no_won_shim)
                except:
                    product_price=''

            try:
                status = driver.find_element_by_css_selector('.SaleLabel').text
            except:
                status = ""

            # 엑셀에 작성
            ws.append([write_date, status, product_title, url, product_price])

            # 뒤로가기
            driver.back()
            driver.switch_to.frame('cafe_main')

        # 다음 게시글 page 이동
        pages = driver.find_elements_by_css_selector('.prev-next a')[page + 1]
        pages.click()
    driver.find_element_by_css_selector('.m-tcol-c').click()


# selenium 끝내고 엑셀 파일 저장
driver.quit()
wb.save(f'중고나라 {today}{thing} 매물.xlsx')

# 가격이 비이상적인 데이터 삭제하기
df = pd.read_excel(f'C:\\Users\\82102\\PycharmProjects\\CoditFrist\\news\\mail\\중고나라 2021-04-07맥북 m1 매물.xlsx')

q1 = df['가격'].quantile(0.25)
q3 = df['가격'].quantile(0.75)
iqr = q3 - q1

condition = (df['가격'] > q3 + 1.5 * iqr) | (df['가격'] < q1 - 1.5 * iqr)
df.drop(df[condition].index, inplace=True)


