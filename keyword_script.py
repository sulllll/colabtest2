import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time

# 구글 스프레드시트 인증 및 시트 열기
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
client = gspread.authorize(creds)
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1-nbdmcfrw9OjLtJ7_21-XhOa25hddHrcy2qLVS7assc/edit?usp=sharing'
sheet = client.open_by_url(spreadsheet_url).worksheet('A')

# ChromeOptions 설정
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

def process_keyword(row):
    driver = webdriver.Chrome(options=options)
    driver.get('https://whereispost.com/keyword')

    try:
        keyword = sheet.cell(row, 1).value
        if not keyword:
            print(f"Row {row} is empty.")
            driver.quit()
            return False  # 빈 키워드인 경우 루프 중지 신호

        # 입력 필드 찾기 및 입력
        input_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'input#keyword'))
        )
        input_field.clear()
        input_field.send_keys(keyword)
        input_field.send_keys(Keys.RETURN)  # 엔터 키 입력으로 검색 실행

        # 결과가 로드될 때까지 대기
        time.sleep(7)

        # 전체 페이지 HTML 가져오기
        page_source = driver.page_source

        # BeautifulSoup로 파싱
        soup = BeautifulSoup(page_source, 'html.parser')

        # 결과 테이블 찾기
        result_table = soup.find("table", {"id": "result"})
        if result_table:
            rows = result_table.find_all("tr")
            for table_row in rows:
                columns = table_row.find_all("td")
                if len(columns) >= 5:
                    keyword = columns[1].get_text().strip()
                    pc_search_volume = columns[2].get_text().strip()
                    mobile_search_volume = columns[3].get_text().strip()
                    total_search_volume = columns[4].get_text().strip()
                    document_count = columns[5].get_text().strip()
                    percentage = columns[6].get_text().strip()

                    if keyword:
                        print(f"키워드: {keyword}, PC 검색량: {pc_search_volume}, 모바일 검색량: {mobile_search_volume}, 총 조회수: {total_search_volume}, 문서수: {document_count}, 비율: {percentage}")

                        # 구글 시트에 데이터 업데이트
                        sheet.update_cell(row, 4, keyword)  # E 열에 PC 검색량 저장
                        sheet.update_cell(row, 5, pc_search_volume)  # E 열에 PC 검색량 저장
                        sheet.update_cell(row, 6, mobile_search_volume)  # F 열에 모바일 검색량 저장
                        sheet.update_cell(row, 7, total_search_volume)  # G 열에 총 조회수 저장
                        sheet.update_cell(row, 8, document_count)  # H 열에 문서수 저장
                        sheet.update_cell(row, 9, percentage)  # I 열에 비율 저장
        else:
            print(f"결과 테이블 또는 행을 찾을 수 없습니다. Row {row}")

        print(f"성공적으로 {keyword}에 대한 데이터를 추출했습니다.")
        return True  # 루프 계속 신호

    except Exception as e:
        print(f"예외 발생 ({keyword}):", str(e))
        sheet.update_cell(row, 10, f"오류: {str(e)}")  # J 열에 오류 메시지 저장
        return True  # 루프 계속 신호

    finally:
        driver.quit()

for row in range(2, 102):
    if not process_keyword(row):
        break  # 데이터가 없는 경우 루프 중지
    time.sleep(2)  # 키워드 마스터 새로고침 대기 시간
    print(f"키워드 마스터 새로고침. Row {row} 완료.")
