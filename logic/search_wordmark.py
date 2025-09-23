import os
import time

import pandas as pd
from playwright.sync_api import sync_playwright, Page

from helpers.captcha_solver import read_captcha


def fill_form_fields(page: Page, wordmark: str, trademark_class: int):
    """Fill the wordmark and class fields"""
    # Fill in the wordmark field using exact field name
    wordmark_input = page.locator('input[name="ctl00$ContentPlaceHolder1$TBWordmark"]')
    wordmark_input.fill(wordmark)
    print(f"Entered wordmark: {wordmark}")
    
    # Fill in the class field using exact field name
    class_input = page.locator('input[name="ctl00$ContentPlaceHolder1$TBClass"]')
    class_input.fill(str(trademark_class))
    print(f"Entered class: {trademark_class}")


def get_captcha_image(page: Page):
    """Detect and save CAPTCHA image, return filename if found"""
    captcha_images = page.locator('img')
    filenames = []
    
    # Check for CAPTCHA image (look for images that might be CAPTCHA)
    for i in range(captcha_images.count()):
        img = captcha_images.nth(i)
        src = img.get_attribute('src')
        if src and ('captcha' in src.lower() or 'cap' in src.lower() or src.startswith('data:image')):
            print("\n" + "="*50)
            print("CAPTCHA DETECTED!")
            
            # Save CAPTCHA image
            try:
                # Create captcha directory if it doesn't exist
                if not os.path.exists('captcha'):
                    os.makedirs('captcha')
                
                # Generate filename with timestamp
                timestamp = int(time.time())
                filename = f"captcha/captcha_{timestamp}.png"
                
                # Take screenshot of the CAPTCHA image
                img.screenshot(path=filename)
                print(f"CAPTCHA image saved as: {filename}")
                return filename
                        
            except Exception as e:
                print(f"Could not save CAPTCHA image: {e}")
                return None
    
    # If no specific CAPTCHA found, check for any suspicious images
    all_images = page.locator('img')
    if all_images.count() > 1:  # If there are multiple images, one might be CAPTCHA
        print("Checking for possible CAPTCHA images...")
        # Save all images to be safe
        try:
            if not os.path.exists('captcha'):
                os.makedirs('captcha')
            
            timestamp = int(time.time())
            for i in range(all_images.count()):
                img = all_images.nth(i)
                try:
                    filename = f"captcha/possible_captcha_{timestamp}_{i}.png"
                    img.screenshot(path=filename)
                    print(f"Saved possible CAPTCHA image: {filename}")
                    filenames.append(filename)
                except Exception:
                    pass
            
            # Return the first saved image
            if filenames:
                print("Using first saved image as CAPTCHA")
                return filenames[0]
                            
        except Exception as e:
            print(f"Could not save images: {e}")
    
    return None


def solve_captcha_with_retry(page: Page, wordmark: str, trademark_class: int, max_retries: int = 5):
    """
    Attempt to solve CAPTCHA with retry mechanism
    
    Args:
        page: Playwright page object
        wordmark: The trademark word/phrase
        trademark_class: The class number
        max_retries: Maximum number of CAPTCHA retry attempts
    
    Returns:
        bool: True if successful, False if failed after all retries
    """
    for attempt in range(max_retries):
        print(f"\n--- CAPTCHA Attempt {attempt + 1}/{max_retries} ---")
        
        # Get CAPTCHA image
        captcha_filename = get_captcha_image(page)
        
        if not captcha_filename:
            print("No CAPTCHA image found. Continuing without CAPTCHA.")
            return True
        
        try:
            # Solve CAPTCHA
            captcha_code = read_captcha(captcha_filename)
            print(f"CAPTCHA solved: {captcha_code}")
            
            # Clear any existing CAPTCHA input and fill new code
            captcha_input = page.locator('input[name="ctl00$ContentPlaceHolder1$captcha1"]')
            captcha_input.clear()
            captcha_input.fill(captcha_code)
            print(f"Entered CAPTCHA code: {captcha_code}")
            
            # Click the Search button
            search_button = page.locator('input[value="Search"]')
            if search_button.is_visible():
                search_button.click()
                print("Clicked Search button")
                
                # Wait for response
                page.wait_for_timeout(3000)
                
                # Check if we're still on the same page (indicating CAPTCHA failure)
                # or if we've moved to results page (indicating success)
                current_url = page.url
                
                # If we're still on the search form page, check for error messages
                if "frmmain.aspx" in current_url:
                    # Look for CAPTCHA error or new CAPTCHA image
                    # If form fields are still filled, it means CAPTCHA was wrong
                    wordmark_field = page.locator('input[name="ctl00$ContentPlaceHolder1$TBWordmark"]')
                    
                    if wordmark_field.input_value() == wordmark:
                        print("❌ CAPTCHA appears to be incorrect (form fields retained)")
                        if attempt < max_retries - 1:
                            print("Retrying with new CAPTCHA...")
                            continue
                        else:
                            print("❌ Maximum CAPTCHA retry attempts reached")
                            return False
                    else:
                        # Fields were cleared, might need to refill form
                        print("Form fields were cleared, refilling...")
                        fill_form_fields(page, wordmark, trademark_class)
                        continue
                else:
                    # We're on a different page, likely results page
                    print("✅ CAPTCHA solved successfully! Moved to results page.")
                    page.wait_for_load_state('networkidle')
                    return True
            else:
                print("Search button not found!")
                return False
                
        except Exception as e:
            print(f"Error during CAPTCHA attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                print("Retrying...")
                # Refresh the page to get a new CAPTCHA
                page.reload()
                page.wait_for_load_state('networkidle')
                fill_form_fields(page, wordmark, trademark_class)
                continue
            else:
                print("❌ Maximum CAPTCHA retry attempts reached")
                return False
    
    return False


def extract_trademark_results(page: Page):
    """
    Extract trademark search results from the table
    
    Args:
        page: Playwright page object
    
    Returns:
        pd.DataFrame: DataFrame containing extracted results
    """
    results = []
    
    # Wait for the results table to be present
    table_selector = "table#ContentPlaceHolder1_MGVSearchResult"
    
    try:
        # Check if table exists
        if not page.locator(table_selector).is_visible():
            print("No results table found")
            return pd.DataFrame(results)
        
        # Get all data rows (skip header row)
        rows = page.locator(f"{table_selector} tbody tr.row")
        row_count = rows.count()
        
        print(f"Found {row_count} trademark records")
        
        for i in range(row_count):
            row = rows.nth(i)
            
            try:
                # Extract data from each row
                record = {}
                
                # Get serial number
                sl_no_element = row.locator("span[id*='LblSlNo']")
                record['serial_number'] = sl_no_element.text_content().strip() if sl_no_element.is_visible() else ""
                
                # Get wordmark
                wordmark_element = row.locator("span[id*='lblsimiliarmark']")
                record['wordmark'] = wordmark_element.text_content().strip() if wordmark_element.is_visible() else ""
                
                # Get proprietor name
                proprietor_element = row.locator("span[id*='LblVProprietorName']")
                record['proprietor'] = proprietor_element.text_content().strip() if proprietor_element.is_visible() else ""
                
                # Get application number
                app_number_element = row.locator("span[id*='lblapplicationnumber']")
                record['application_number'] = app_number_element.text_content().strip() if app_number_element.is_visible() else ""
                
                # Get class/classes
                class_element = row.locator("span[id*='lblsearchclass']")
                record['class_name'] = class_element.text_content().strip() if class_element.is_visible() else ""
                
                # Get status
                status_element = row.locator("span[id*='Label6']")
                record['status'] = status_element.text_content().strip() if status_element.is_visible() else ""
                
                # Get show details link (if needed)
                details_link = row.locator("a[id*='LnkShowDetails']")
                record['has_details_link'] = details_link.is_visible()
                
                # Get image link info
                image_link = row.locator("a[id*='LnkDGImage']")
                record['has_image'] = image_link.is_visible()
                
                if record['has_image']:
                    # Extract application number from image link for later use
                    onclick_attr = image_link.get_attribute('onclick')
                    if onclick_attr and 'appl_no=' in onclick_attr:
                        # Extract application number from onclick attribute
                        import re
                        app_no_match = re.search(r'appl_no=(\d+)', onclick_attr)
                        if app_no_match:
                            record['image_app_number'] = app_no_match.group(1)
                
                # Check if record has meaningful data before adding
                if any(record.values()):
                    results.append(record)
                    print(f"Extracted record {i+1}: {record['wordmark']} - {record['application_number']}")
                
            except Exception as e:
                print(f"Error extracting data from row {i+1}: {str(e)}")
                continue
    
    except Exception as e:
        print(f"Error extracting table data: {str(e)}")
    
    return pd.DataFrame(results)


def search_trademark(wordmark: str, trademark_class: int, max_captcha_retries: int = 5, headless: bool = False):
    """
    Automate trademark search on Indian IP office website
    
    Args:
        wordmark (str): The trademark word/phrase to search for
        trademark_class (str): The class number for the trademark
        max_captcha_retries (int): Maximum number of CAPTCHA retry attempts
    """
    with sync_playwright() as p:
        # Launch browser (you can set headless=False to see the browser)
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        
        try:
            print("Navigating to the trademark search website...")
            page.goto("https://tmrsearch.ipindia.gov.in/tmrpublicsearch/frmmain.aspx")
            
            # Wait for page to load completely
            page.wait_for_load_state('networkidle')
            
            print("Page loaded. Filling in the form...")
            
            # Fill form fields
            fill_form_fields(page, wordmark, str(trademark_class))
            
            # Wait a moment for any dynamic content to load
            page.wait_for_timeout(1000)
            
            # Attempt to solve CAPTCHA with retry mechanism
            success = solve_captcha_with_retry(page, wordmark, trademark_class, max_captcha_retries)
            
            if success:
                print("✅ Search completed successfully! Results should now be displayed.")
                df = extract_trademark_results(page)
                return df
            else:
                print("❌ Failed to complete search after multiple CAPTCHA attempts.")
                return None
                
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            
        finally:
            browser.close()


if __name__ == "__main__":
    wordmark = "DEVICE OF PROTEC"
    trademark_class = 9
    max_captcha_retries = 5  # You can adjust this number
    
    print("\nStarting search for:")
    print(f"Wordmark: {wordmark}")
    print(f"Class: {trademark_class}")
    print(f"Max CAPTCHA retries: {max_captcha_retries}")
    print("-" * 40)
    
    search_trademark(wordmark, trademark_class, max_captcha_retries)
