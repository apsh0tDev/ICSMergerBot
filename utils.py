from fp.fp import FreeProxy
from flagged import banned_proxies
import requests

def get_proxy():
    response = requests.get("https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all")
    print(response.text)