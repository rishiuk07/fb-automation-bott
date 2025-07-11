import time
import json
import os
import requests
import datetime
import pandas as pd
import schedule
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# === CONFIG ===
GOOGLE_SHEET_URL = 'https://script.google.com/macros/s/PASTE_YOUR_SHEET_SCRIPT_URL/exec'
COOKIES_FILE = 'facebook_cookies.json'
CHROMEDRIVER_PATH = 'chromedriver'  # For Linux on Railway, no .exe

# === Load Cookies ===
def load_cookies(driver, cookies_file):
    with open(cookies_file, 'r') as file:
        cookies = json.load(file)
    for cookie in cookies:
        driver.add_cookie(cookie)

# === Facebook Post Automation ===
def post_to_facebook(caption, image_url):
    print("🟢 Starting browser...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=chrome_options)

    driver.get("https://www.facebook.com/")
    time.sleep(5)
    driver.delete_all_cookies()
    load_cookies(driver, COOKIES_FILE)
    driver.refresh()
    time.sleep(5)

    # ✅ Change this to your Page URL
    driver.get("https://www.facebook.com/profile.php?id=61576557846721")
    time.sleep(5)

    # Click Photo/Video post button
    try:
        photo_btn = driver.find_element(By.XPATH, "//span[contains(text(), 'Photo/video')]")
        photo_btn.click()
        time.sleep(4)
    except Exception as e:
        print("❌ Failed to click photo button:", e)
        driver.quit()
        return

    # Download image to temp
    img_path = "temp.jpg"
    try:
        img_data = requests.get(image_url).content
        with open(img_path, 'wb') as handler:
            handler.write(img_data)
    except:
        print("❌ Image download failed.")
        return

    # Upload the image
    try:
        file_input = driver.find_element(By.XPATH, "//input[@type='file']")
        file_input.send_keys(os.path.abspath(img_path))
        time.sleep(6)
    except Exception as e:
        print("❌ Could not upload image:", e)
        driver.quit()
        return

    # Enter the caption
    try:
        caption_box = driver.find_element(By.XPATH, "//div[@aria-label='Write a post…']")
        caption_box.click()
        caption_box.send_keys(caption)
        time.sleep(2)
    except:
        print("❌ Could not find caption box")
        driver.quit()
        return

    # Click Post
    try:
        post_button = driver.find_element(By.XPATH, "//div[@aria-label='Post']")
        post_button.click()
        print("✅ Post done!")
        time.sleep(5)
    except:
        print("❌ Failed to click Post button")

    driver.quit()

# === Scheduler ===
def check_sheet():
    print("🔄 Checking Sheet...")
    try:
        data = requests.get(GOOGLE_SHEET_URL).json()
        df = pd.DataFrame(data[1:], columns=data[0])
        now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        for index, row in df.iterrows():
            scheduled = f"{row['Date']} {row['Time']}"
            if scheduled == now:
                print(f"🕒 Match found for {scheduled}")
                post_to_facebook(row['Caption'], row['Image URL'])
    except Exception as e:
        print("❌ Error reading Sheet:", e)

# Schedule to check every minute
schedule.every(1).minutes.do(check_sheet)

print("🚀 Automation started... (Running forever)")
while True:
    schedule.run_pending()
    time.sleep(30)
