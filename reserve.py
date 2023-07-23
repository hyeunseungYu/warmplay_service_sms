import reserve_macro_firefox

from datetime import datetime
import time


while True:
    print(f"{datetime.now().strftime('%H:%M:%S')} 작동합니다")
    reserve_macro_firefox.f_get_list()  #리스트 크롤링
    time.sleep(300)  # 반복 주기