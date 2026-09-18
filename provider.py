import requests
import re
from datetime import datetime, timezone, timedelta

SOURCE_URL = "https://raw.githubusercontent.com/raid35/docs/main/SPORT_UROP.m3u"

OUTPUT_FILE = "stv2.m3u"
LOG_FILE    = "stv2.log"

HEADER = '#EXTM3U url-tvg="https://raw.githubusercontent.com/didikc/EPG-8/main/epg.xml.gz"'

# Channels to always exclude
BLACKLIST = ["caze tv 1", "caze tv 2", "mlb", "nfl", "dude"]

# Channels to prepend at the very top
PREPEND_CHANNELS = [
    '''#EXTINF:-1 tvg-logo="https://raw.githubusercontent.com/iprtl/p1/master/logo/skysportpl.png" ,Sky Sports Premier League
#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
https://bl.rutube.ru/livestream/e5bacac3b8e730791d4cab20ae81cd8f/index.m3u8?s=supMvSCVCg69RtHgOfv1Kg&e=2089026853&scheme=https''',

    '''#EXTINF:-1 tvg-logo="https://raw.githubusercontent.com/iprtl/p1/master/logo/skysportpl.png" ,Sky Sports Premier League
#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
https://bl.rutube.ru/livestream/e5bacac3b8e730791d4cab20ae81cd8f/index.m3u8?s=qd2MUJx2uKe8vQ1n81yoEA&e=2088940274&scheme=https'''
]

def download(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.text
    except requests.RequestException as e:
        print(f"❌ Failed: {url}\n{e}")
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

def is_block_allowed(block):
    if not block:
        return False
    header = block[0].lower()
    for bad in BLACKLIST:
        if bad in header:
            return False
    return True

def clean_extinf(line):
    # Remove unwanted attributes
    line = re.sub(r'\s*group-title="[^"]+"', '', line, flags=re.IGNORECASE)
    line = re.sub(r'\s*tvg-id="[^"]+"', '', line, flags=re.IGNORECASE)
    line = re.sub(r'\s*tvg-name="[^"]+"', '', line, flags=re.IGNORECASE)
    line = re.sub(r'\s*tvg-logo="[^"]+"', '', line, flags=re.IGNORECASE)
    line = line.replace("|", "")
    line = line.replace(",,", ",")

    if "," in line:
        channel_name = line.split(",", 1)[-1].strip()
        channel_name_norm = channel_name.title()

        # Custom replacements
        if channel_name_norm.lower() == "tnt sports 1":
            return '#EXTINF:-1 tvg-id="TNTSports1.uk@HD" tvg-logo="https://raw.githubusercontent.com/didikc/TV-Logo/main/logos/tnt-sports-1-uk.png" ,TNT Sports 1'
        elif channel_name_norm.lower() == "tnt sports 2":
            return '#EXTINF:-1 tvg-id="TNTSports2.uk@HD" tvg-logo="https://raw.githubusercontent.com/didikc/TV-Logo/main/logos/tnt-sports-2-uk.png" ,TNT Sports 2'
        elif channel_name_norm.lower() == "tnt sports 3":
            return '#EXTINF:-1 tvg-id="TNTSports3.uk@HD" tvg-logo="https://raw.githubusercontent.com/didikc/TV-Logo/main/logos/tnt-sports-3-uk.png" ,TNT Sports 3'
        elif channel_name_norm.lower() == "premier sports 1":
            return '#EXTINF:-1 tvg-id="PremierSports1.ie@HD" tvg-logo="https://i.imgur.com/eOybZMU.png" ,Premier Sports 1'
        elif channel_name_norm.lower() == "premier sports 2":
            return '#EXTINF:-1 tvg-id="PremierSports2.ie@HD" tvg-logo="https://i.imgur.com/Fx1n84p.png" ,Premier Sports 2'
        elif channel_name_norm.lower() == "sportv 1":
            return '#EXTINF:-1 tvg-id="SportTV1.pt@SD" tvg-logo="https://i.imgur.com/YWic36u.png" ,Sportv 1'
        elif channel_name_norm.lower() == "sportv 2":
            return '#EXTINF:-1 tvg-id="SportTV2.pt@SD" tvg-logo="https://i.imgur.com/0jSR6yG.png" ,Sportv 2'
        elif channel_name_norm.lower() == "sportv 3":
            return '#EXTINF:-1 tvg-id="SportTV3.pt@SD" tvg-logo="https://i.imgur.com/6Dw3GUx.png" ,Sportv 3'
        elif channel_name_norm.lower() == "tsn 1":
            return '#EXTINF:-1 tvg-id="TSN1.ca@SD" tvg-logo="https://i.imgur.com/eRFE0jZ.png" ,TSN 1'
        elif channel_name_norm.lower() == "tsn 4":
            return '#EXTINF:-1 tvg-id="TSN4.ca@SD" tvg-logo="https://i.imgur.com/qJyAWU8.png" ,TSN 4'
        elif channel_name_norm.lower() == "mutv":
            return '#EXTINF:-1 tvg-id="MUTV.uk@SD" tvg-logo="https://i.imgur.com/3lFfYzY.png" ,MUTV'
        else:
            return f"#EXTINF:-1,{channel_name_norm}"
    return line

def main():
    log_entries = [f"Run started at {datetime.now().isoformat()}"]
    try:
        content = download(SOURCE_URL)
        entries = parse_m3u(content)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            # Write header
            f.write(HEADER + "\n")

            # Write the two Sky Sports Premier League entries first
            for block in PREPEND_CHANNELS:
                f.write(block + "\n")

            # Write the rest of the parsed channels
            for block in entries:
                if not is_block_allowed(block):
                    continue
                cleaned = clean_extinf(block[0])
                f.write(cleaned + "\n")
                for line in block[1:]:
                    f.write(line + "\n")

        log_entries.append(f"✅ Playlist written to {OUTPUT_FILE}")
    except Exception as e:
        log_entries.append(f"❌ Error: {e}")

    with open(LOG_FILE, "w", encoding="utf-8") as logf:
        logf.write("\n".join(log_entries))

if __name__ == "__main__":
    main()
