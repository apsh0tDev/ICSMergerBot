import os
import base64
import requests
from dotenv import load_dotenv
from supabase import create_client, Client
import pyshorteners

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
email = os.getenv("SUPABASE_EMAIL")
password = os.getenv("SUPABASE_PASSWORD")
supabase: Client = create_client(url, key)
bucket_name = "calendars"

async def upload_to_supabase(ics, txt):
    ics_exists = os.path.exists(ics)
    txt_exists = os.path.exists(txt)
    txt_file_name = os.path.basename(txt)
    ics_file_name = os.path.basename(ics)

    if ics_exists and txt_exists:
                 #Upload txt
        with open(txt, "rb") as file:
            response_txt = supabase.storage.from_(bucket_name).upload(txt_file_name, file)

        #Upload ics
        with open(ics, "rb") as file:
            response_ics = supabase.storage.from_(bucket_name).upload(ics_file_name, file)

        if response_txt.status_code == 200:
            print("Txt successfully uploaded.")
        else:
                print(f"Failed to upload TXT file. Status code: {response_txt.status_code}")
                print("Response:", response_txt.json())

        if response_ics.status_code == 200:
            print("ICS successfully uploaded.")
        else:
                print(f"Failed to upload TXT file. Status code: {response_ics.status_code}")
                print("Response:", response_ics.json())

        if response_ics.status_code == 200 and response_txt.status_code == 200:
             return "Success"
        else:
             return "Error uploading files"
        

async def getPublicUrl(file_path):
     data = supabase.storage.from_(bucket_name).get_public_url(file_path)
     url = pyshorteners.Shortener().owly.short(data)
     return url
         
#DEPRECATED
async def upload_files_to_github(ics, txt, token):
    ics_exists = os.path.exists(ics)
    txt_exists = os.path.exists(txt)

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    if ics_exists and txt_exists:

        #Upload txt
        with open(txt, "rb") as file:
            content_txt = base64.b64encode(file.read()).decode()
        
        data = {
            "message" : f"Add {ics}",
            "committer": {
                "name": "apsh0tDev",
                "email": "apsh0t@proton.me"  
            },
            "content": content_txt
        }
        url = f"https://api.github.com/repos/apsh0tDev/ICSMerger_calendars/contents/{txt}"
        response_txt = requests.put(url, json=data, headers=headers)

        #Upload ics
        with open(ics, "rb") as file:
            content_ics = base64.b64encode(file.read()).decode()
        
        data = {
            "message" : f"Add {ics}",
            "committer": {
                "name": "apsh0tDev",
                "email": "apsh0t@proton.me"  
            },
            "content": content_ics
        }
        url = f"https://api.github.com/repos/apsh0tDev/ICSMerger_calendars/contents/{ics}"
        response_ics = requests.put(url, json=data, headers=headers)

        if response_txt.status_code == 201:
            print("Txt successfully uploaded.")
        else:
                print(f"Failed to upload TXT file. Status code: {response_txt.status_code}")
                print("Response:", response_txt.json())

        if response_ics.status_code == 201:
            print("ICS successfully uploaded.")
        else:
                print(f"Failed to upload TXT file. Status code: {response_ics.status_code}")
                print("Response:", response_ics.json())

        if response_ics.status_code == 201 and response_txt.status_code == 201:
             return "Success"
        else:
             return "Error uploading files"