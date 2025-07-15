
import asyncio
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from telegram import Bot
from telegram.constants import ParseMode

# === CONFIGURATION === #
BOT_TOKEN = "write ur api key here of telegram channel"
CHANNEL_USERNAME = "@jobsdedo"
TELEGRAM_POST_LIMIT = 10

# === SETUP HEADLESS CHROME === #
def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/91.0.4472.124 Safari/537.36"
    )
    return webdriver.Chrome(options=options)

# === FORMATTER === #
def format_job(job):
    return f"""
📢 {job['Company']} Started Hiring

🧑‍💻 Role: | {job['Role']}  
🎓 Batch: | {job['Batch']}  
💰 Salary: | {job['Salary']}  
📍 Location: | {job['Location']}  
🔰 Experience: | {job['Experience']}  
📚 Qualification: | {job['Qualification']}  
🔗 Apply: | {job['Link']}
"""

# === TELEGRAM CHANNEL SCRAPER WITH SCROLLING === #
def scrape_telegram_channels():
    channels = [
        "https://t.me/s/fresheroffcampus",
        "https://t.me/s/freshopenings",
        "https://t.me/s/fresherjobsadda",
        "https://t.me/s/freshercareersdotin",
        "https://t.me/s/job4fresherss",
        "https://t.me/s/govtjobs9",
        "https://t.me/s/gocareers",
        "https://t.me/s/jobsinternshipswale",
        "https://t.me/s/offcampus_phodenge",
        "https://t.me/s/findITJobsLink"
    ]

    all_jobs = []

    for url in channels:
        print(f"🔎 Scraping channel: {url}")
        driver = setup_driver()
        driver.get(url)
        time.sleep(5)

        last_height = driver.execute_script("return document.body.scrollHeight")
        for i in range(8):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        messages = driver.find_elements(By.CSS_SELECTOR, "div.tgme_widget_message_text")
        print(f"🧪 Extracted {len(messages)} messages from this channel.")

        for msg in messages:
            if len(all_jobs) >= TELEGRAM_POST_LIMIT:
                break

            try:
                text = msg.text.strip()
                lines = text.splitlines()

                job = {
                    "Company": "Not Mentioned",
                    "Role": "Not Mentioned",
                    "Batch": "Not Mentioned",
                    "Salary": "Not Mentioned",
                    "Location": "Not Mentioned",
                    "Experience": "Not Mentioned",
                    "Qualification": "Not Mentioned",
                    "Link": "Not Mentioned"
                }

                for line in lines:
                    lower_line = line.lower()
                    if "role:" in lower_line:
                        job["Role"] = line.split(":", 1)[1].strip()
                    elif "batch:" in lower_line:
                        job["Batch"] = line.split(":", 1)[1].strip()
                    elif "salary:" in lower_line:
                        job["Salary"] = line.split(":", 1)[1].strip()
                    elif "location:" in lower_line:
                        job["Location"] = line.split(":", 1)[1].strip()
                    elif "experience:" in lower_line:
                        job["Experience"] = line.split(":", 1)[1].strip()
                    elif "qualification:" in lower_line:
                        job["Qualification"] = line.split(":", 1)[1].strip()
                    elif "apply:" in lower_line or "link:" in lower_line:
                        job["Link"] = line.split(":", 1)[1].strip()
                    elif "hiring" in lower_line:
                        job["Company"] = line.split()[0].strip()

                all_jobs.append(job)
            except Exception as e:
                print("⚠️ Failed to parse message:", e)
                continue

        driver.quit()

        if len(all_jobs) >= TELEGRAM_POST_LIMIT:
            break

    return all_jobs[:TELEGRAM_POST_LIMIT]

# === TELEGRAM POSTER === #
async def post_to_telegram(jobs):
    bot = Bot(token=BOT_TOKEN)
    for job in jobs:
        formatted = format_job(job)
        try:
            await bot.send_message(chat_id=CHANNEL_USERNAME, text=formatted, parse_mode=ParseMode.MARKDOWN)
            await asyncio.sleep(2)
        except Exception as e:
            print("❌ Failed to post a job:", e)

# === MAIN === #
if __name__ == "__main__":
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting job scrape from multiple Telegram channels...")
    jobs = scrape_telegram_channels()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Found {len(jobs)} jobs. Posting to Telegram...")
    asyncio.run(post_to_telegram(jobs))
    print("✅ Done")
