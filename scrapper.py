import os
from dotenv import load_dotenv
import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

load_dotenv()

# Actual scraper
def site_scrapper(url):
    chrome_driver = os.environ.get("WEB_DRIVER")
    options = webdriver.ChromeOptions()
    # Recommended: Run headless for servers
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(service=Service(chrome_driver), options=options)
    try:
        driver.get(url)
        print(f"Scraping content from {url}")
        html = driver.page_source
        return html
    finally:
        driver.quit()

def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    return str(body_content) if body_content else ""

def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, "html.parser")
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()
    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )
    return cleaned_content

def split_dom_content(dom_content, max_length=80000):
    return [dom_content[i : i + max_length] for i in range(0, len(dom_content), max_length)]
