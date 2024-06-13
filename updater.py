import os
import time
import random
import asyncio
import aiohttp
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


def main():
    data = supabase.storage.from_(bucket_name).list()
    calendars_content = []
    for item in data:
        if item['name'].endswith('txt'):
            response = supabase.storage.from_(bucket_name).download(item['name'])
            text_content = response.decode('utf-8')

            print(f"""Updating calendars from: {item['name']}
            ## ----------""")
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
    print("Cycle done.")

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
                    response = requests.get(url=url, headers=headers, proxies=proxy_list, verify=False)
                else:
                    response = requests.get(url=url, headers=headers)
                print("Status: ", response.status_code)

                content = response.text
                return content   

            except Exception as e:
                print("Error fetching data", e)
                print(f"Attempt ({attempt_count + 1}/{max_attempts})")
            attempt_count += 1
            time.sleep(1)
        return None


schedule.cyclic(dt.timedelta(minutes=3), get_proxies)
schedule.cyclic(dt.timedelta(minutes=10), main)

if __name__ == "__main__":
    start = get_proxies()
    if start == "Done":
        main()

while True:
    schedule.exec_jobs()
    time.sleep(1)