import requests
from bs4 import BeautifulSoup
import json

def scrape_mangoplate_events():
    url = "https://www.mangoplate.com/search/이벤트"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print("❌ 페이지 로딩 실패:", res.status_code)
        return

    soup = BeautifulSoup(res.text, "html.parser")
    results = []

    for li in soup.select("ul.list-restaurants > li"):
        name_tag = li.select_one("h2.title > a")
        desc_tag = li.select_one("p.etc")

        if name_tag:
            name = name_tag.text.strip()
            desc = desc_tag.text.strip() if desc_tag else "이벤트 진행 중"

            results.append({
                "name": name,
                "event": desc,
                "lat": None,
                "lng": None
            })

    with open("static/events.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(results)}개 이벤트 저장 완료")

if __name__ == "__main__":
    scrape_mangoplate_events()
