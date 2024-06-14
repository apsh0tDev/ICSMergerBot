import re
import os
import glob
import time
import random
import asyncio
import requests
import datetime as dt
from supabase import create_client, Client
from dotenv import load_dotenv
from fake_useragent import UserAgent
from scheduler import Scheduler
from ics import Calendar



load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
email = os.getenv("SUPABASE_EMAIL")
password = os.getenv("SUPABASE_PASSWORD")
supabase: Client = create_client(url, key)
bucket_name = "calendars"
schedule = Scheduler()
proxies = []

def get_proxies():
    print("Getting proxies")
    data = requests.get("https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all")
    lines = data.text.splitlines()
    global proxies
    for line in lines:
        proxy = f"http://{line}"
        proxies.append(proxy)
    print("Proxies done")
    return "Done"

def clean_up():
    directory_path = "./"
    ics_files = glob.glob(os.path.join(directory_path, '*.ics'))
    
    for file_path in ics_files:
        try:
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

def run_main():
    asyncio.run(main())

async def main():
    clean_up()
    data = supabase.storage.from_(bucket_name).list()
    calendars_content = []
    for item in data:
        if item['name'].endswith('txt'):
            response = supabase.storage.from_(bucket_name).download(item['name'])
            text_content = response.decode('utf-8')
            print(f"""Updating calendars from: {item['name']}""")
            lines = text_content.splitlines()
            for line in lines:
                use_proxy = False
                url = line.strip()
                if "rentals.tripadvisor" in url:
                    use_proxy = True
                try:
                    ics = fetch_data(url=url, use_proxy=use_proxy)
                    if ics != None:
                        calendars_content.append(ics)
                except Exception as e:
                    print("ERROR: ", e) 
            file_name_no_ext = item['name'].replace(".txt", "")
            new_cal = merge(content=calendars_content, file_name=file_name_no_ext)
            await find_and_replace(f"{file_name_no_ext}.ics", new_cal)

    print("Cycle done.")


#Get data for each URL

def fetch_data(url, max_attempts=3, use_proxy=False):
    print(f"Fetching data from: {url}")
    ua = UserAgent()
    attempt_count = 0
    if len(proxies) > 0:
        while attempt_count < max_attempts:
            try:
                headers = {
                    'User-Agent': ua.random,
                    'Accept': 'text/calendar',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Connection': 'keep-alive',
                    'Referer': 'http://www.google.com/',                
                }
                proxy = random.choice(proxies)
                proxy_list = {
                    'http' : proxy,
                }
                if use_proxy:
                    print("Using proxy: ", proxy_list)
                    response = requests.get(url=url, headers=headers, proxies=proxy_list)
                else:
                    response = requests.get(url=url, headers=headers)
                print("Status: ", response.status_code)

                if response.status_code == 200:
                    content = response.text
                else:
                    content = None

                return content   

            except Exception as e:
                print("Error fetching data", e)
                print(f"Attempt ({attempt_count + 1}/{max_attempts})")
            attempt_count += 1
            time.sleep(1)
        return None
    
#Merge function    
def merge(content, file_name):
    print("Merging content from: ", file_name)
    merged_calendar = Calendar()

    for item in content:
        cal = Calendar(item)
        merged_calendar.events.update(cal.events)

    merged_calendar_str = merged_calendar.serialize()
    return merged_calendar_str


schedule.cyclic(dt.timedelta(minutes=3), get_proxies)
schedule.cyclic(dt.timedelta(minutes=2), run_main)

#Function to find the X-WR-CALNAME and use it in the new calendar
def find_calname(text):
    pattern = r'X-WR-CALNAME:\s*(.+)'
    match = re.search(pattern, text)
    if match:
        print("FOUND IT!")
        return match.group(1).strip()
    else:
        print("FOUND NOTHING 😔")
        return None

#Finds the corresponding .ics file and replaces it
async def find_and_replace(file, cal):
    ics = supabase.storage.from_(bucket_name).download(file)
    content = ics.decode('utf-8')
    calendar_name = find_calname(content)
    if calendar_name != None:
        #Add the name and timezone
        calendar_lines = cal.splitlines()

        for i, line in enumerate(calendar_lines):
            if line.startswith("BEGIN:VCALENDAR"):
                calendar_lines.insert(i + 1, f"X-WR-CALNAME:{calendar_name}")
                calendar_lines.insert(i + 1, f"X-WR-TIMEZONE:America/New_York")
                break
        merged_calendar_with_name = "\n".join(calendar_lines)
        
        supabase.storage.from_(bucket_name).remove(file)
        
        with open(file, 'w') as f:
            f.write(merged_calendar_with_name)
        
        await upload_to_supabase(file)

async def upload_to_supabase(ics):
    ics_exists = os.path.exists(ics)
    ics_file_name = os.path.basename(ics)

    if ics_exists:
        with open(ics, "rb") as file:
            try:
                response_ics = supabase.storage.from_(bucket_name).upload(ics_file_name, file)
                if response_ics.status_code == 200:
                    print("Calendar successfully uploaded")
                else:
                    print("Failed to upload ICS file")
            except Exception as e:
                print("ERROR DETAIL: ", e)
 
if __name__ == "__main__":
    start = get_proxies()
    if start == "Done":
       asyncio.run(main())
while True:
    schedule.exec_jobs()
    time.sleep(1)