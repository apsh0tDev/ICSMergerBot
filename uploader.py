import os
import base64
import requests

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