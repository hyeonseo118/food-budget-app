import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def scrape_naver_place_events(keyword="혜화 맛집", max_results=10):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # 네이버 지도 접속
    driver.get("https://map.naver.com/v5/")

    time.sleep(2)

    # 검색창 찾기
    search_box = driver.find_element(By.CSS_SELECTOR, "input.input_search")
    search_box.send_keys(keyword)
    search_box.send_keys("\n")

    time.sleep(5)

    # iframe 전환
    try:
        driver.switch_to.frame(driver.find_element(By.CSS_SELECTOR, "iframe#searchIframe"))
        time.sleep(2)
    except:
        print("iframe 접근 실패")
        driver.quit()
        return []

    # 식당 목록 크롤링
    names = []
    try:
        items = driver.find_elements(By.CSS_SELECTOR, "ul>li .place_bluelink")
        for item in items[:max_results]:
            name = item.text.strip()
            link = item.get_attribute("href")
            names.append({"name": name, "link": link})
    except Exception as e:
        print("식당 목록 추출 실패:", e)
    finally:
        driver.quit()

    return names

if __name__ == "__main__":
    data = scrape_naver_place_events()
    for idx, d in enumerate(data, 1):
        print(f"{idx}. {d['name']} - {d['link']}")
