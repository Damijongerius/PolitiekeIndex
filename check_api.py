import urllib.request
import re

url = "https://www.verkiezingsprogrammasdownloaden.nl/api/parties"
headers = {"User-Agent": "Mozilla/5.0"}

for endpoint in ["/api/parties", "/api/manifestos", "/api/programs"]:
    try:
        full_url = "https://www.verkiezingsprogrammasdownloaden.nl" + endpoint
        req = urllib.request.Request(full_url, headers=headers)
        res = urllib.request.urlopen(req)
        data = res.read().decode('utf-8')
        print(f"Endpoint {endpoint}: SUCCESS ({len(data)} bytes)")
        print(data[:300])
    except Exception as e:
        print(f"Endpoint {endpoint}: {e}")
