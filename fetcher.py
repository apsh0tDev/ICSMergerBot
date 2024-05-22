import asyncio
from fp.fp import FreeProxy
from fake_useragent import UserAgent
import aiohttp

async def fetch_ics_data(url):
    try:
        proxy = FreeProxy().get()
        ua = UserAgent()
        user_agent = ua.random
        print("User-Agent:", user_agent)
        
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/calendar',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Referer': 'http://www.google.com/',
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, proxy=proxy) as response:
                print("Status:", response.status)
                if response.status == 200 and response.headers.get('content-type', '').startswith('text/calendar'):
                    ics_content = await response.text()
                    print("ICS Content:", ics_content)
                else:
                    print("Unexpected Content-Type:", response.headers.get('content-type'))
                    body = await response.text()
                    print("Body:", body[:500])

    except Exception as e:
        print("An error occurred:", str(e))

if __name__ == "__main__":
    asyncio.run(fetch_ics_data('https://ical.booking.com/v1/export?t=aed179e5-4730-461c-a129-0f04b84b2948'))
