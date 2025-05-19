import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def scrape_and_save(keyword="혜화 맛집", save_path="data/events.json", max_results=10):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://map.naver.com/v5/")
    time.sleep(2)

    search_box = driver.find_element(By.CSS_SELECTOR, "input.input_search")
    search_box.send_keys(keyword)
    search_box.send_keys("\n")
    time.sleep(5)

    try:
        driver.switch_to.frame(driver.find_element(By.CSS_SELECTOR, "iframe#searchIframe"))
        time.sleep(2)
    except:
        driver.quit()
        return []

    results = []
    try:
        items = driver.find_elements(By.CSS_SELECTOR, "ul>li .place_bluelink")
        for item in items[:max_results]:
            name = item.text.strip()
            link = item.get_attribute("href")
            results.append({"name": name, "link": link})
    except:
        pass
    finally:
        driver.quit()

    # ✅ 'data/' 폴더가 없으면 자동 생성
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"[✔] events.json 자동 저장 완료 ({len(results)}개)")

# (선택) 단독 실행 테스트
if __name__ == "__main__":
    scrape_and_save()
