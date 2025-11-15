# Run this once to save the HTML
import requests
from pathlib import Path

url = "https://gameofthrones.fandom.com/wiki/Jon_Snow"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0',
    'DNT': '1'
}

# Try from your browser first - sometimes manual saves work better
response = requests.get(url, headers=headers)

if response.status_code == 200:
    Path("mock_wiki.html").write_text(response.text, encoding="utf-8")
    print("✓ Saved successfully")
else:
    print(f"✗ Status: {response.status_code}")
