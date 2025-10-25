#Scraping
import sys
print(sys.executable)

import time
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

# -------------------------
# CONFIGURATION
# -------------------------
BASE_URLS = [
    "https://bankofmaharashtra.in/personal-banking/loans/home-loan",
    "https://bankofmaharashtra.in/pradhan-mantri-awas-yojana-2",
    "https://bankofmaharashtra.in/mahabank-vehicle-loan-scheme-for-two-wheelers-loans",
    "https://bankofmaharashtra.in/topup-home-loan",
    "https://bankofmaharashtra.in/gold-loan",
    "https://bankofmaharashtra.in/maha-super-flexi-housing-loan-scheme",
    "https://bankofmaharashtra.in/personal-banking/loans/car-loan",
    "https://bankofmaharashtra.in/mahabank-vehicle-loan-scheme-for-second-hand-car",
    "https://bankofmaharashtra.in/educational-loans",
    "https://bankofmaharashtra.in/personal-banking/loans/personal-loan"
]

OUTPUT_JSON = "data_raw/loans_bom.json"
WAIT_TIME = 3  # seconds between requests

# Selenium driver setup (for dynamic content)
chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
driver_path = r"C:\Program Files\chromedriver-win64\chromedriver.exe"
service = ChromeService(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# -------------------------
# HELPER FUNCTIONS
# -------------------------

def scrape_tab_content(tab_element, loan_name="Home Loan"):
    """
    Clicks a tab and scrapes tables, lists, paragraphs inside that tab.
    """
    tab_name = tab_element.text.strip()
    print(f"Scraping tab: {tab_name}")
    
    try:
        tab_element.click()
    except Exception as e:
        print(f"Could not click tab {tab_name}: {e}")
        return []
    
    time.sleep(WAIT_TIME)  # wait for content to load
    
    # Parse current page content
    soup = BeautifulSoup(driver.page_source, "html.parser")
    all_content = []

    # 1️⃣ Scrape tables
    tables = soup.find_all("table")
    for table in tables:
        df = pd.read_html(str(table))[0]
        all_content.append({
            "loan_name": loan_name,
            "tab_name": tab_name,
            "table_data": df.to_dict(orient="records")
        })

    # 2️⃣ Scrape lists and paragraphs
    sections = soup.find_all(['p', 'li'])
    for sec in sections:
        text = sec.get_text(strip=True)
        if len(text) > 20:
            all_content.append({
                "loan_name": loan_name,
                "tab_name": tab_name,
                "text": text
            })
    
    return all_content

# -------------------------
# MAIN SCRAPING
# -------------------------
for url in BASE_URLS:
    driver.get(url)
    time.sleep(WAIT_TIME)  # initial page load

    all_loans_data = []

    # Find all sub-tabs (update the selector if the site uses different structure)
    try:
        tab_elements = driver.find_elements(By.CSS_SELECTOR, "ul.nav-tabs li a")
        if not tab_elements:
            print("No tabs found. Scraping entire page as fallback.")
            all_loans_data.extend(scrape_tab_content(driver.find_element(By.TAG_NAME, "body")))
        else:
            for tab in tab_elements:
                tab_content = scrape_tab_content(tab)
                all_loans_data.extend(tab_content)
    except Exception as e:
        print(f"Error detecting tabs: {e}")
        # Fallback: scrape whole page
        soup = BeautifulSoup(driver.page_source, "html.parser")
        all_loans_data.append({
            "loan_name": "Home Loan",
            "tab_name": "Full Page Fallback",
            "text": soup.get_text(strip=True)
        })

# -------------------------
# SAVE OUTPUT
# -------------------------
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(all_loans_data, f, indent=4, ensure_ascii=False)

print(f"Scraping completed. Total records: {len(all_loans_data)}")
print(f"Data saved to {OUTPUT_JSON}")

driver.quit()
