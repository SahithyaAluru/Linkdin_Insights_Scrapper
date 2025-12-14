import requests
import re
import os
from bs4 import BeautifulSoup
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COOKIE_FILE = os.path.join(BASE_DIR, "linkedin_cookies.txt")

def clean_int(text):
    if not text:
        return None
    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else None

def load_cookies(driver):
    if not os.path.exists(COOKIE_FILE):
        raise Exception("linkedin_cookies.txt not found")

    with open(COOKIE_FILE, "r", encoding="utf-8") as file:
        for line in file:
            if line.startswith("#") or not line.strip():
                continue

            parts = line.strip().split("\t")
            if len(parts) >= 7:
                driver.add_cookie({
                    "domain": parts[0],
                    "path": parts[2],
                    "name": parts[5],
                    "value": parts[6]
                })

def scrape_linkedin_page(page_id: str):
    url = f"https://www.linkedin.com/company/{page_id}/"
    response = requests.get(url, headers=HEADERS, timeout=20)

    if response.status_code != 200:
        raise Exception("LinkedIn page not accessible")

    soup = BeautifulSoup(response.text, "html.parser")

    data = {
        "page_name": None,
        "page_url": url,
        "linkedin_id": page_id,
        "profile_picture": None,
        "description": None,
        "website": None,
        "industry": None,
        "followers": None,
        "head_count": None
    }

    h1 = soup.find("h1")
    if h1:
        data["page_name"] = h1.get_text(strip=True)

    meta_desc = soup.find("meta", {"name": "description"})
    if meta_desc:
        desc = meta_desc.get("content")
        data["description"] = desc
        match = re.search(r"([\d,]+)\s+followers", desc)
        if match:
            data["followers"] = clean_int(match.group(1))

    img = soup.find("meta", property="og:image")
    if img:
        data["profile_picture"] = img.get("content")

    for dt in soup.find_all("dt"):
        label = dt.get_text(strip=True).lower()
        dd = dt.find_next_sibling("dd")
        if not dd:
            continue

        val = dd.get_text(strip=True)

        if "industry" in label:
            data["industry"] = val
        elif "website" in label:
            data["website"] = val.split("External")[0]
        elif "company size" in label:
            data["head_count"] = clean_int(val)

    print("SCRAPED PAGE DATA", data)
    return data

def scrape_company_posts(page_id, max_posts=10):
    url = f"https://www.linkedin.com/company/{page_id}/posts/"

    options = Options()

    options.add_argument("--start-maximized")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.get(url)
    sleep(8)
    for _ in range(6):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    posts_data = []

    posts = soup.find_all(
        "div",
        class_="ember-view occludable-update",
        limit=max_posts
    )

    print("POSTS FOUND", len(posts))

    for post in posts:
        try:
            text = post.find("span", class_="break-words")
            likes = post.find(
                "span",
                class_="social-details-social-counts__reactions-count"
            )
            comments = post.find(
                "span",
                class_="social-details-social-counts__comments"
            )

            posts_data.append({
                "content": text.get_text(strip=True) if text else "",
                "likes": int(re.sub(r"\D", "", likes.get_text())) if likes else 0,
                "comments_count": int(re.sub(r"\D", "", comments.get_text())) if comments else 0
            })
        except:
            continue

    return posts_data
