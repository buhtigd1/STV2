import requests
import re
from datetime import datetime

SOURCE_URL = "https://raw.githubusercontent.com/raid35/docs/main/SPORT_UROP.m3u"
OUTPUT_FILE = "stv2.m3u"
LOG_FILE    = "stv2.log"

HEADER = '#EXTM3U'

# Channels to prepend at the very top
PREPEND_CHANNELS = [
    '''#EXTINF:-1 ,Sky Sports Premier League
#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
https://bl.rutube.ru/livestream/e5bacac3b8e730791d4cab20ae81cd8f/index.m3u8?s=supMvSCVCg69RtHgOfv1Kg&e=2089026853&scheme=https''',

    '''#EXTINF:-1 ,Sky Sports Premier League
#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
https://bl.rutube.ru/livestream/e5bacac3b8e730791d4cab20ae81cd8f/index.m3u8?s=qd2MUJx2uKe8vQ1n81yoEA&e=2088940274&scheme=https'''
]

def log(message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {message}\n")
    print(message)

def download(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.text
    except requests.RequestException as e:
        log(f"❌ Failed to download: {url}\n{e}")
        return ""

def clean_extinf(line):
    # Remove unwanted attributes
    line = re.sub(r'\s*tvg-id="[^"]+"', '', line, flags=re.IGNORECASE)
    line = re.sub(r'\s*group-title="[^"]+"', '', line, flags=re.IGNORECASE)
    line = re.sub(r'\s*tvg-logo="[^"]+"', '', line, flags=re.IGNORECASE)
    line = re.sub(r'\s*tvg-name="[^"]+"', '', line, flags=re.IGNORECASE)
    line = re.sub(r'\s*\w+-title="[^"]+"', '', line, flags=re.IGNORECASE)

    # Normalize EXTINF line
    if line.startswith("#EXTINF"):
        # Ensure proper comma separation
        if "," not in line:
            parts = line.split(' ', 1)
            if len(parts) == 2:
                line = parts[0] + "," + parts[1]
        # Force standard prefix
        line = re.sub(r'^#EXTINF.*?-1', '#EXTINF:-1', line)

    return line.strip()

def main():
    log("Downloading playlist...")
    source = download(SOURCE_URL)
    if not source:
        log("No content downloaded.")
        return

    log("Processing playlist...")
    lines = source.splitlines()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        # Write header
        f.write(HEADER + "\n")

        # Write cleaned playlist
        for line in lines:
            if line.startswith("#EXTINF"):
                f.write(clean_extinf(line) + "\n")
            else:
                f.write(line.strip() + "\n")

    log(f"✅ Done: saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()




