import os
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, JavascriptException

UPLOAD_URL = "https://www.temp.kotol.cloud/"
FILE_PATH = os.path.expanduser("~/Pictures/smart-file-uploader/isi-logo.png")

#Fixed screenshot directory path
LOG_DIR = "logs"
SCREENSHOT_DIR = r"C:\Users\Kalilinux\Pictures\smart-file-uploader\Screenshots"

# Ensure directories exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "activity.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log(msg):
    print(msg)
    logging.info(msg)

chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-notifications")
service = Service()
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    log("Opening upload page...")
    driver.get(UPLOAD_URL)
    wait = WebDriverWait(driver, 25)

    # Try to locate upload field in multiple ways
    try:
        upload_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
        )
        driver.execute_script("arguments[0].style.display='block';", upload_input)
        log("Found <input type='file'> element.")
    except TimeoutException:
        log("No direct <input type='file'> found. Trying to click upload button...")
        try:
            upload_btn = driver.find_element(By.XPATH, "//button[contains(.,'Upload') or contains(.,'Choose File')]")
            upload_btn.click()
            time.sleep(2)
            upload_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            driver.execute_script("arguments[0].style.display='block';", upload_input)
        except Exception:
            raise TimeoutException("No upload element found.")

    # Upload the file
    log(f"Uploading file: {FILE_PATH}")
    upload_input.send_keys(FILE_PATH)
    time.sleep(2)

    # Wait for upload progress
    try:
        wait.until(EC.presence_of_element_located((By.ID, "uploadProgressText")))
        log("Upload progress bar detected.")
    except TimeoutException:
        log("Upload progress not visible. Continuing anyway...")

    # Wait for code to apppear
    log("Waiting for uploaded code to appear inside #table...")
    try:
        wait.until(lambda d: d.find_element(By.ID, "table").text.strip() != "")
        log("Code detected inside #table.")
    except TimeoutException:
        log("Timeout waiting for code content — capturing full page for debug.")
        fullshot = os.path.join(SCREENSHOT_DIR, "timeout_fullpage.png")
        driver.save_screenshot(fullshot)
        log(f"Full-page screenshot saved to: {fullshot}")
        raise

    # Screenshot Section
    codes = driver.find_element(By.ID, "codes")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    section_shot = os.path.join(SCREENSHOT_DIR, f"codes_section_{timestamp}.png")
    codes.screenshot(section_shot)
    log(f"Screenshot saved successfully: {section_shot}")

except Exception as e:
    log(f"Error: {e}")
finally:
    log("Process complete. Closing browser.")
    driver.quit()
