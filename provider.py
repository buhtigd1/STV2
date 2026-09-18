import requests
import logging
import re
from datetime import datetime

SOURCE_URL = "https://raw.githubusercontent.com/raid35/docs/main/SPORT_UROP.m3u"
OUTPUT_FILE = "stv2.m3u"
LOG_FILE = "stv2.log"

HEADER = '#EXTM3U url-tvg="https://raw.githubusercontent.com/didikc/EPG-8/main/epg.xml.gz"'

# Channels to prepend at the very top
PREPEND_CHANNELS = [
    '''#EXTINF:-1 tvg-logo="https://raw.githubusercontent.com/iprtl/p1/master/logo/skysportpl.png" ,Sky Sports Premier League
#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
https://bl.rutube.ru/livestream/e5bacac3b8e730791d4cab20ae81cd8f/index.m3u8?s=supMvSCVCg69RtHgOfv1Kg&e=2089026853&scheme=https''',

    '''#EXTINF:-1 tvg-logo="https://raw.githubusercontent.com/iprtl/p1/master/logo/skysportpl.png" ,Sky Sports Premier League
#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
https://bl.rutube.ru/livestream/e5bacac3b8e730791d4cab20ae81cd8f/index.m3u8?s=qd2MUJx2uKe8vQ1n81yoEA&e=2088940274&scheme=https'''
]

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def download(url):
    try:
        logging.info(f"Starting download: {url}")
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        logging.info("Download successful")
        return r.text
    except requests.RequestException as e:
        logging.error(f"Download failed: {e}")
        return ""

def clean_line(line: str) -> str:
    # Remove group-title attribute
    line = re.sub(r'\s*group-title="[^"]+"', '', line, flags=re.IGNORECASE)
    # Remove decorative separator lines (lots of '=' and text in between)
    if re.match(r'^\s*=+\s*.*\s*=+\s*$', line):
        return ""  # drop the line entirely
    return line

def main():
    logging.info("=== Scraper run started ===")
    source = download(SOURCE_URL)

    if not source:
        logging.warning("No content downloaded, exiting.")
        return

    cleaned_lines = ["#EXTM3U"]  # ensure header at the very first line
    for line in source.splitlines():
        if line.startswith("#EXTINF") or re.match(r'^\s*=+', line):
            line = clean_line(line)
        if line.strip():  # skip empty lines after cleaning
            cleaned_lines.append(line)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(cleaned_lines))

    logging.info(f"Playlist saved to {OUTPUT_FILE} with header #EXTM3U")
    logging.info("=== Scraper run finished ===")

if __name__ == "__main__":
    main()
