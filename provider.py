import requests
import re
from datetime import datetime

SOURCE_URL = "https://raw.githubusercontent.com/raid35/docs/main/SPORT_UROP.m3u"
OUTPUT_FILE = "stv2.m3u"
LOG_FILE    = "stv2.log"

HEADER = '#EXTM3U url-tvg="https://raw.githubusercontent.com/didikc/EPG-8/main/epg.xml.gz"'

def download(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.text
    except requests.RequestException as e:
        log(f"❌ Failed to download: {url}\n{e}")
        return ""

def parse_m3u(content):
    lines = content.splitlines()
    entries = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF"):
            block = [line]
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                block.append(next_line)
                if not next_line.startswith("#"):
                    break
                j += 1
            entries.append(block)
            i = j
        else:
            i += 1
    return entries

def clean_extinf(line):
    # Remove group-title and other unwanted attributes
    line = re.sub(r'\s*group-title="[^"]+"', '', line, flags=re.IGNORECASE)
    return line

def log(message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {message}\n")
    print(message)

def main():
    log("Downloading playlist...")
    source = download(SOURCE_URL)

    if not source:
        log("No content downloaded.")
        return

    log("Parsing playlist...")
    entries = parse_m3u(source)
    log(f"Total channels found: {len(entries)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n")
        for block in entries:
            for line in block:
                if line.startswith("#EXTINF"):
                    f.write(clean_extinf(line) + "\n")
                else:
                    f.write(line + "\n")

    log(f"✅ Done: saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
