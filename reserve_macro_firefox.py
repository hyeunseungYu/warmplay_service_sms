from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException

from datetime import datetime
import time

import smtplib
from email.message import EmailMessage

from sdk.api.message import Message
from sdk.exceptions import CoolsmsException

import re

import json

# api 정보가 있는 JSON 파일 열기
with open('api_data.json') as f:
    data = json.load(f)

site_url = 'https://partner.booking.naver.com/bizes/938469/booking-list-view'
board_list = []  # 크롤링 결과 저장 리스트
p_board_list = []  # 이전 크롤링 결과 저장 리스트
first_execution = True  # 처음 실행 여부를 나타내는 변수

# 저장할 프로필 경로
profile_path = "/Users/yuhyeonseung/Library/Application Support/Firefox/Profiles/don5dw4z.forSelenium_warmplay"

def f_get_list():
    global first_execution
    try:

        # Firefox 프로필 가져오기
        firefox_profile = FirefoxProfile(profile_path)

        # Firefox 옵션 설정
        firefox_options = Options()
        firefox_options.profile = firefox_profile

        firefox_options.add_argument("--headless")


        # Firefox 실행
        firefox_service = Service(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=firefox_service,options=firefox_options)

        driver.maximize_window()

        driver.get(site_url)
        time.sleep(5)    
        
        all_lists_1 = driver.find_element(By.CLASS_NAME, 'BookingListView__list__3dEpl.BookingListView__table__2DWDa')
        all_lists_2 = all_lists_1.find_element(By.CLASS_NAME, 'BookingListView__list-contents__1mfa8')

        time.sleep(0.5)
        target_lists = all_lists_2.find_elements(By.CSS_SELECTOR, '.BookingListView__contents-inner__2lnqC.d-flex.flex-nowrap')
        time.sleep(0.5)

        for target in target_lists:
            inner_div = target.find_element(By.CLASS_NAME, 'BookingListView__contents-user__1BF15.d-flex.align-items-stretch.flex-nowrap')
            name = inner_div.find_element(By.CLASS_NAME, 'align-self-center.BookingListView__cell__10Lyz.BookingListView__name__16_zV').text
            book_number = inner_div.find_element(By.CLASS_NAME, 'align-self-center.BookingListView__cell__10Lyz.BookingListView__book-number__pJ808').text
            phone_number = inner_div.find_element(By.CLASS_NAME, 'align-self-center.BookingListView__cell__10Lyz.BookingListView__phone__2IoIp').text
            phone_number = phone_number.replace("-","")
            
            board_list.append('이름: ' + name +'\n예약번호: '+ book_number +'\n핸드폰번호: ' + phone_number)
        

        # 처음 실행이 아니라면 이전 예약 건들과 비교하여 새로운 예약 건이 있는지 확인
        if not first_execution:
            send_target_list = list(set(board_list) - set(p_board_list))
            send_sms(send_target_list, 'test')
            send_email(send_target_list)  # 새로운 예약 건 메일 전송

        first_execution = False
        p_board_list.clear()
        p_board_list.extend(board_list)  # 현재 예약 건들을 이전 예약 건들로 업데이트
        board_list.clear()

        
        
        driver.quit()
    
    except NoSuchElementException as nse:
        print(f"{datetime.now().strftime('%H:%M:%S')} 에러 발생 내용입니다.\nNoSuchElementException이 발생했습니다.")

        SMTP_SERVER = 'smtp.gmail.com'
        SMTP_PORT = 465
        smtp = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)

        email_addr = "warmplay93@gmail.com"
        email_pass = data['email_pass']

        smtp.login(email_addr, email_pass)

        message = EmailMessage()
        message.set_content(f"{board_list}")
        message["Subject"] = f"{datetime.now().strftime('%H:%M:%S')} 에러 발생 내용입니다.\nNoSuchElementException이 발생했습니다."

        message["From"] = email_addr
        message["To"] = 'hyeunseung03@gmail.com'

        smtp.send_message(message)

        return str(nse), type(nse).__name__
    
    except WebDriverException as we:
        print(f"{datetime.now().strftime('%H:%M:%S')} 에러 발생 내용입니다.\nWebDriverException이 발생했습니다.")

        SMTP_SERVER = 'smtp.gmail.com'
        SMTP_PORT = 465
        smtp = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)

        email_addr = "warmplay93@gmail.com"
        email_pass = data['email_pass']

        smtp.login(email_addr, email_pass)

        message = EmailMessage()
        message.set_content(f"{board_list}")
        message["Subject"] = f"{datetime.now().strftime('%H:%M:%S')} 에러 발생 내용입니다.\nWebDriverException이 발생했습니다."
    
        message["From"] = email_addr
        message["To"] = 'hyeunseung03@gmail.com'

        smtp.send_message(message)

        return str(we), type(we).__name__

    except Exception as e:
        print(f"{datetime.now().strftime('%H:%M:%S')} 에러 발생 내용입니다.\n알 수 없는 예외가 발생했습니다.")

        SMTP_SERVER = 'smtp.gmail.com'
        SMTP_PORT = 465
        smtp = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)

        email_addr = "warmplay93@gmail.com"
        email_pass = data['email_pass']

        smtp.login(email_addr, email_pass)

        message = EmailMessage()
        message.set_content(f"{board_list}")
        message["Subject"] = f"{datetime.now().strftime('%H:%M:%S')} 에러 발생 내용입니다.\n알 수 없는 예외가 발생했습니다. 로그를 확인해 주세요."
    
        message["From"] = email_addr
        message["To"] = 'hyeunseung03@gmail.com'

        smtp.send_message(message)
        print(str(e), type(e))

        return str(e), type(e).__name__
        

    def send_email(board_list):
        SMTP_SERVER = 'smtp.gmail.com'
        SMTP_PORT = 465
        smtp = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)

        email_addr = "warmplay93@gmail.com"
        email_pass = data['email_pass']

        smtp.login(email_addr, email_pass)

        if len(board_list) > 0:
            print(f'{datetime.now().strftime("%Y%m%D %H:%M:%S")} 새로운 예약 건이 있습니다.')
            print()
        
            message = EmailMessage()
            message.set_content(f"{board_list}")
            message["Subject"] = f"{datetime.now().strftime('%H:%M:%S')} 예약 내역입니다. 총 {len(board_list)}건입니다."
        
            message["From"] = email_addr
            message["To"] = 'warmplay93@gmail.com'

            smtp.send_message(message)
        else:
            print(f"{datetime.now().strftime('%Y%m%D %H:%M:%S')} 예약 건이 없습니다.")
            print()

        smtp.quit()



def send_sms(board_list, message_text):
    ## set api key, api secret
    api_key = data['sms_api_key']
    api_secret = data['sms_secret_key']

    if len(board_list) > 0:
        print(f'{datetime.now().strftime("%Y%m%D %H:%M:%S")} 새로운 예약 건에 대한 메시지 발송을 준비합니다.')
        print()

        for board in board_list:
            to_number = re.search(r'010[-\.\s]?\d{4}[-\.\s]?\d{4}', board).group()
            to_name = re.search(r'이름: (.*)\n', board).group(1)

            ## 4 params(to, from, type, text) are mandatory. must be filled
            params = dict()
            params['type'] = 'lms' # Message type ( sms, lms, mms, ata )
            params['to'] = to_number # Recipients Number '01000000000,01000000001'
            params['from'] = '01034003766' # Sender number
            params['text'] = f'''안녕하세요😃\n{to_name} 님. 웜플레이를 예약해주셔서 감사합니다.\n웜플레이의 현관문 비밀번호는 9331* 이며 \n빨간 벽돌집 조그만 계단 위쪽 1.5층 나무문을 열고 들어오시면 됩니다.\n화장실은 1층 계단 바로 아래 오른쪽이며 냉장고 안의 물은 인당 1병씩 제공됩니다.\n웜플레이의 자세한 이용 안내는 아래 링크 클릭하시어 읽어 보실 수 있습니다.\nhttp://naver.me/FEd9WJ7Z\n감사합니다. 즐거운 시간 되세요 :)''' # Message

            cool = Message(api_key, api_secret)
            try:
                response = cool.send(params)
                print("Success Count : %s" % response['success_count'])
                print("Error Count : %s" % response['error_count'])
                print("Group ID : %s" % response['group_id'])

                if "error_list" in response:
                    print("Error List : %s" % response['error_list'])

            except CoolsmsException as e:
                print("Error Code : %s" % e.code)
                print("Error Message : %s" % e.msg)


if __name__ == "__main__":
    f_get_list()