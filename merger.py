import re
import asyncio
import aiohttp
from fp.fp import FreeProxy
from fake_useragent import UserAgent
from ics import Calendar
from datetime import datetime

async def process_file(file):
    content = file.read().decode('utf-8')
    lines = content.splitlines()

    invalid_urls = []
    valid_urls = []
    proxy = FreeProxy(https=True).get()
    ua = UserAgent()
    data = []

    for line in lines:
        url = line.strip()
        if not re.match(r'^https?://', url):
            invalid_urls.append(url)
        else:
            valid_urls.append(url)
    for url in valid_urls:
        try:
            ics = await asyncio.create_task(fetch_ics_data(url=url, proxy=proxy, ua=ua.random))
            data.append(ics)
        except Exception as e:
            print(e)
    
    cal = await merger(data=data)
    with open(cal['name'], 'w') as f:
        f.write(cal['data'])

    return cal['name']

async def fetch_ics_data(url, proxy, ua):
    print(f"Fetching data from: {url}")
    print(f"Proxy: {proxy}")
    print(f"User Agent: {ua}")
    attempt_count = 0
    while attempt_count < 3:
        try:
            headers = {
                'User-Agent': ua,
                'Accept': 'text/calendar',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Referer': 'http://www.google.com/',                
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, proxy=proxy) as response:
                    print("Status: ", response.status)
                    if response.status == 200 and response.headers.get('content-type', '').startswith('text/calendar'):
                        ics_content = await response.text()
                        return ics_content
                    else:
                        print("Unexpected Content-Type:", response.headers.get('content-type'))
                        body = await response.text()
                        print("Body:", body[:500])
                        attempt_count += 1
        except Exception as e:
            print("An error occurred:", str(e))
            attempt_count += 1

        
async def merger(data):
    merged_calendar = Calendar()

    for item in data:
        cal = Calendar(item)
        merged_calendar.events.update(cal.events)
    
    calendar_name = "Merger Calendar"
    merged_calendar_str = merged_calendar.serialize()
    calendar_lines = merged_calendar_str.splitlines()

    for i, line in enumerate(calendar_lines):
        if line.startswith("BEGIN:VCALENDAR"):
            calendar_lines.insert(i + 1, f"X-WR-CALNAME:{calendar_name}")
            break

    merged_calendar_with_name = "\n".join(calendar_lines)
    now = datetime.now()
    formatted_date_time = now.strftime('%Y%m%d%H%M')
    calendar_filename = f"merged_calendar_{formatted_date_time}.ics"

    calmerged = {
        "name" : calendar_filename,
        "data" : merged_calendar_with_name
    }

    return calmerged