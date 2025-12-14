from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from time import sleep
from bs4 import BeautifulSoup

def scrape_company_posts(page_id, max_posts=15):
    url = f"https://www.linkedin.com/company/{page_id}/posts/"
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.get(url)
    sleep(5)
    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(3)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()
    posts_data = []

    posts = soup.find_all("div", class_="ember-view occludable-update", limit=max_posts)

    for post in posts:
        try:
            text = post.find("span", class_="break-words")
            post_text = text.get_text(strip=True) if text else ""

            link = post.find("a", href=True)
            post_url = "https://www.linkedin.com" + link["href"] if link else ""

            likes = post.find("span", class_="social-details-social-counts__reactions-count")
            likes_count = likes.get_text(strip=True) if likes else "0"

            comments = post.find("span", class_="social-details-social-counts__comments")
            comments_count = comments.get_text(strip=True) if comments else "0"

            posts_data.append({
                "post_text": post_text,
                "post_url": post_url,
                "likes": likes_count,
                "comments": comments_count
            })

        except Exception as e:
            print("Error parsing post:", e)

    return posts_data

if __name__ == "__main__":
    page_id = "deepsolv"   
    posts = scrape_company_posts(page_id, max_posts=15)
    for i, post in enumerate(posts, 1):
        print(f"\nPost {i}")
        print(post)
