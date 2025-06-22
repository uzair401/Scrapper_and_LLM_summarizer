import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
from dotenv import load_dotenv
import os

load_dotenv()


#Actual scrapper
def site_scrapper(url):
    
    # Common ChromeDriver location on Windows
    chrome_driver = os.environ.get("WEB_DRIVER")
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(chrome_driver), options=options)
    try:
        driver.get(url)
        print(f"Scraping content from {url}")
        html = driver.page_source
        
        return html
    finally:
        driver.quit()
        
from bs4 import BeautifulSoup

def extract_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    body = soup.body
    if body:
        return str(body)
    return False

def clean_body_data(body):
    soup = BeautifulSoup(body, 'html.parser') 
    
    
