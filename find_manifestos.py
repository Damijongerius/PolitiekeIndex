import urllib.request
import re

url = "https://www.verkiezingsprogrammasdownloaden.nl/assets/index-B0ckuM9U.js"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
content = urllib.request.urlopen(req).read().decode("utf-8", errors="ignore")

print("Length of JS:", len(content))
matches = re.findall(r'/objects/manifestos/[^\s"\']+\.pdf', content)
print("Matches:", set(matches))
