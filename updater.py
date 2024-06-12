import os
from supabase import create_client, Client
from dotenv import load_dotenv
from rich import print
import asyncio
import requests
from ics import Calendar

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
email = os.getenv("SUPABASE_EMAIL")
password = os.getenv("SUPABASE_PASSWORD")
supabase: Client = create_client(url, key)
bucket_name = "calendars"

async def main():
    # Sign in using email and password
    #user = supabase.auth.sign_in_with_password({"email": email, "password": password})
    data = supabase.storage.from_(bucket_name).list()
    for item in data:
        if item['name'].endswith('txt'):
            #Getting the text file
            response = supabase.storage.from_(bucket_name).download(item['name'])
            text_content = response.decode('utf-8')
            merged_calendar = Calendar()

            #But we need the url list individually:
            url_list = [url.strip() for url in text_content.split('\n') if url.strip()]
            for url in url_list:
                try:
                    ics_data = await fetch_ics_data(url=url)
                except Exception as e:
                    print("Error: ", e)
                    continue
                if ics_data != "Error": 
                    calendar = Calendar(ics_data)
                    merged_calendar.events.update(calendar.events)
                else:
                    print("Error getting this calendar")
            
            ics_file_name = item['name'][:-4] + '.ics'
            if any(file['name'] == ics_file_name for file in data):
                await delete_previous_file(ics_file_name)
            else:
                print("File not found")
    print(merged_calendar)
            
            
import time

async def fetch_ics_data(url):
    print("Getting calendar from: ", url)
    max_retries = 3
    retry_delay = 2  # seconds
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                # Check if the response content starts with 'BEGIN:VCALENDAR'
                if response.text.startswith('BEGIN:VCALENDAR'):
                    return response.text
                else:
                    print("Invalid iCalendar format")
                    return "Error"
            else:
                print("Non-200 status code:", response.status_code)
                retries += 1
                print(f"Retrying ({retries}/{max_retries})...")
                time.sleep(retry_delay)
        except Exception as e:
            print(e)
            retries += 1
            print(f"Retrying ({retries}/{max_retries})...")
            time.sleep(retry_delay)
    print("Max retries exceeded")
    return "Error"


async def delete_previous_file(file_name):
    print("Deleting file: ", file_name)
    try:
        supabase.storage.from_(bucket_name).remove('calendar_test.ics')
        print("File deleted successfully")
    except Exception as e:
        print("Error deleting file:", e)


if __name__ == "__main__":
    asyncio.run(main())