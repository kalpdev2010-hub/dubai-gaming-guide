import os
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

# Contains only the 18 links routed to the Gaming Guide
FEEDS = {
    "ASUS ROG": "https://www.google.com/alerts/feeds/17291303775024850829/8594716954966060996",
    "Logitech G": "https://www.google.com/alerts/feeds/17291303775024850829/5304635819396728132",
    "Valve": "https://www.google.com/alerts/feeds/17291303775024850829/9427201234034513326",
    "Nintendo": "https://www.google.com/alerts/feeds/17291303775024850829/10430992398900948987",
    "PlayStation": "https://www.google.com/alerts/feeds/17291303775024850829/17602452674615626407",
    "Xbox": "https://www.google.com/alerts/feeds/17291303775024850829/6030646844747330193",
    "Alienware": "https://www.google.com/alerts/feeds/17291303775024850829/4282056408381306355",
    "AMD": "https://www.google.com/alerts/feeds/17291303775024850829/4282056408381308246",
    "Anbernic": "https://www.google.com/alerts/feeds/17291303775024850829/9427201234034515140",
    "Corsair": "https://www.google.com/alerts/feeds/17291303775024850829/8919238735868620618",
    "Elgato": "https://www.google.com/alerts/feeds/17291303775024850829/8919238735868619158",
    "HyperX": "https://www.google.com/alerts/feeds/17291303775024850829/8919238735868620256",
    "LG": "https://www.google.com/alerts/feeds/17291303775024850829/3966050588725823454",
    "NVIDIA": "https://www.google.com/alerts/feeds/17291303775024850829/4282056408381305478",
    "Razer": "https://www.google.com/alerts/feeds/17291303775024850829/5304635819396729890",
    "Samsung": "https://www.google.com/alerts/feeds/17291303775024850829/15000369253469530916",
    "Secretlab": "https://www.google.com/alerts/feeds/17291303775024850829/156754864311868267",
    "SteelSeries": "https://www.google.com/alerts/feeds/17291303775024850829/8919238735868620092"
}

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
# Targeting the Gaming repository
REPO = "kalpdev2010-hub/dubai-gaming-guide"

def create_github_issue(title, link, brand):
    url = f"https://api.github.com/repos/{REPO}/issues"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    check_url = f"{url}?labels={urllib.parse.quote(brand)}&state=all"
    try:
        with urllib.request.urlopen(urllib.request.Request(check_url, headers=headers)) as resp:
            existing = json.loads(resp.read().decode())
            if any(issue['title'] == title for issue in existing):
                return
    except Exception:
        pass

    data = json.dumps({"title": title, "body": link, "labels": [brand]}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        urllib.request.urlopen(req)
        print(f"✅ Posted to Radar: {title}")
    except Exception as e:
        print(f"❌ Error: {e}")

for brand, rss_url in FEEDS.items():
    try:
        req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            tree = ET.parse(response)
            root = tree.getroot()
            
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry')[:2]:
                title = entry.find('{http://www.w3.org/2005/Atom}title').text
                raw_link = entry.find('{http://www.w3.org/2005/Atom}link').attrib['href']
                clean_link = raw_link.split('url=')[1].split('&ct=ga')[0] if 'url=' in raw_link else raw_link
                
                create_github_issue(title, clean_link, brand)
    except Exception as e:
        print(f"Error checking {brand}: {e}")
