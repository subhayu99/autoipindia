import re

import pandas as pd
from playwright.sync_api import sync_playwright

from helpers.utils import get_captcha_image
from helpers.captcha_solver import read_captcha


def search_trademark(application_number: str | int, headless: bool = False):
    application_number = str(application_number)
    with sync_playwright() as p:
        # Launch browser (set headless=False to see the browser)
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        page.goto("https://tmrsearch.ipindia.gov.in/eregister/", timeout=100000)
        page.wait_for_load_state('networkidle', timeout=100000)

        page.wait_for_timeout(5000)
        page.frame_locator('frame[name="eregoptions"]').locator('a#btnviewdetails').click()
        page.wait_for_load_state('networkidle', timeout=100000)

        page.frame_locator('frame[name="showframe"]').locator('input#rdb_0').check()
        page.wait_for_timeout(5000)

        page.frame_locator('frame[name="showframe"]').locator('input#applNumber').fill(application_number)
        page.wait_for_timeout(5000)
        
        captcha_filename = get_captcha_image(page.frame_locator('frame[name="showframe"]'))
        captcha_code = read_captcha(captcha_filename)
        page.frame_locator('frame[name="showframe"]').locator('input#captcha1').fill(captcha_code)
        page.frame_locator('frame[name="showframe"]').locator("input#btnView").click()
        page.wait_for_timeout(5000)

        page.frame_locator('frame[name="showframe"]').locator("table#SearchWMDatagrid a").first.click()
        page.wait_for_timeout(5000)
        
        text = page.frame_locator('frame[name="showframe"]').locator('#lblappdetail').inner_text()
        tm_date = re.findall("Date\s*:\s*(\d{2}/\d{2}/\d{4})", text)[0].strip()
        tm_status = re.findall("Status\s*:\s*(.+)", text)[0].strip()
        tm_name = re.findall("TM Applied For\s+(.+)", text)[0].strip()
        tm_class = re.findall("Class\s+(.+)", text)[0].strip()

        print(f"Trademark Name: {tm_name}")
        print(f"Trademark Class: {tm_class}")
        print(f"Trademark Date: {tm_date}")
        print(f"Trademark Status: {tm_status}")
        df = pd.DataFrame(
            {
                "wordmark": [tm_name],
                "application_number": [application_number],
                "class_name": [tm_class],
                "status": [tm_status],
            }
        )

        browser.close()
    return df
    
if __name__ == "__main__":
    application_number = 6562791
    search_trademark(application_number)
