import os
import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv


load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
email = os.getenv("SUPABASE_EMAIL")
password = os.getenv("SUPABASE_PASSWORD")
supabase: Client = create_client(url, key)
bucket_name = "calendars"

async def main():
    data = supabase.storage.from_(bucket_name).list()
    for item in data:
        if item['name'].endswith('txt'):
            response = supabase.storage.from_(bucket_name).download(item['name'])
            text_content = response.decode('utf-8')

            print("Updating calendars from: ", item['name'])
            print(text_content)

if __name__ == "__main__":
    asyncio.run(main())