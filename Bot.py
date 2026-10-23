import requests
from bs4 import BeautifulSoup
import json
import os
import datetime
import random
from telegram.ext import Application, ContextTypes

# توکن از طریق تنظیمات سرور (Environment Variable) خونده میشه
BOT_TOKEN = os.environ.get("BOT_TOKEN", "TOKEN_HERE")
GROUP_CHAT_ID = "@yamahdikampein"

MEMORY_FILE = "sent_hadiths.json"

URLS = [
    "https://bahjat.ir/fa/content/1887",
    "https://www.hadithlib.com/",
    "https://www.hadithlib.com/guides/view/14/%D8%A7%D9%85%D8%A7%D9%85-%D9%85%D9%87%D8%AF%DB%8C-%D8%B9%D9%84%DB%8C%D9%87-%D8%A7%D9%84%D8%B3%D9%84%D8%A7%D9%85",
    "https://fanoos.kowsarblog.ir/65-%D8%AD%D8%AF%DB%8C%D8%AB-%D8%A7%D8%B2-%D8%AD%D8%B6%D8%B1%D8%AA-%D8%A7%D9%85%D8%A7%D9%85-%D9%85%D9%87%D8%AF%DB%8C-%D8%B9%D9%84%DB%8C%D9%87-%D8%A7%D9%84%D8%B3%D9%84%D8%A7%D9%85"
]

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False)

def scrape_url(url):
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        hadiths = []
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if len(text) > 80:
                hadiths.append(text)
        for div in soup.find_all("div", class_=lambda c: c and ("content" in c or "hadith" in c)):
            text = div.get_text(strip=True)
            if len(text) > 80 and text not in hadiths:
                hadiths.append(text)
        return hadiths
    except Exception as e:
        print(f"خطا در {url}: {e}")
        return []

def get_all_hadiths():
    all_h = []
    for url in URLS:
        result = scrape_url(url)
        all_h.extend(result)
    return list(set(all_h))

async def send_hadith(context: ContextTypes.DEFAULT_TYPE):
    print("در حال دریافت حدیث...")
    hadiths = get_all_hadiths()
    if not hadiths:
        print("هیچ حدیثی پیدا نشد!")
        return
    
    memory = load_memory()
    available = [h for h in hadiths if h not in memory]
    if not available:
        memory = []
        available = hadiths
    
    chosen = random.choice(available)
    memory.append(chosen)
    if len(memory) > 100:
        memory.pop(0)
    save_memory(memory)
    
    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=chosen)
    print("ارسال شد ✅")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    jq = app.job_queue
    tz = datetime.timezone(datetime.timedelta(hours=3, minutes=30))
    times = [datetime.time(7, 0), datetime.time(12, 0),
             datetime.time(20, 0), datetime.time(23, 0)]
    for t in times:
        jq.run_daily(send_hadith, time=t, days=(0,1,2,3,4,5,6), tzinfo=tz)
    print("ربات روشن شد. ساعت‌ها: ۷، ۱۲، ۲۰، ۲۳")
    app.run_polling()

if __name__ == "__main__":
    main()
  
