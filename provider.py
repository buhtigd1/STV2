import requests
import re
from datetime import datetime

SOURCE_URL_1 = "https://raw.githubusercontent.com/raid35/docs/main/SPORT_UROP.m3u"
SOURCE_URL_2 = "https://raw.githubusercontent.com/doms9/iptv/refs/heads/default/M3U8/events.m3u8"

OUTPUT_FILE = "stv2.m3u"
LOG_FILE    = "stv2.log"

HEADER = '#EXTM3U url-tvg="https://raw.githubusercontent.com/didikc/EPG-8/main/epg.xml.gz"'

BLACKLIST = ["caze tv 1", "caze tv 2"]

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

def clean_extinf(line):
    # Remove all unwanted attributes
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
            return '#EXTINF:-1 tvg-id="MUTV.uk@SD" tvg-logo="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiDK5wO1M6YOy_2_IuEtYuj25ReGg3p-V3j60gGqa-cd8rz6f9xuH2o4mQVCRN1rApaVMGLT1q-bhDKcYGS4FbkseAgUhNFvAsDug1hI9wg4iFAGY6JAEEHtqsqdSK2A3CaqugX-fctkzTaywaYoaSIY1ZfFQjwdrQX_CNBMT5IpunnbZNpg2QzZuWjcPvt/s700/MUTV.png" ,MUTV HD'
        elif channel_name_norm.lower() == "cbs sports yedek":
            return '#EXTINF:-1 tvg-id="CBSSportsYedek.tr@SD" tvg-logo="https://raw.githubusercontent.com/didikc/TV-Logo/main/logos/cbs-sports-yedek.png" ,CBS Sports Yedek'

        # Default case
        return f"#EXTINF:-1,{channel_name_norm}"
    return line

def is_block_allowed(block, log_entries):
    if not block:
        return False
    header = block[0].lower()
    for bad in BLACKLIST:
        if bad in header:
            log_entries.append(f"BLACKLISTED: {header}")
            return False
    return True

def main():
    print("Downloading playlists...")
    source1 = download(SOURCE_URL_1)
    source2 = download(SOURCE_URL_2)

    print("Parsing playlists...")
    entries1 = parse_m3u(source1)
    entries2 = parse_m3u(source2)

    # Only keep Premier League, Formula 1, England Premier League, or Football channels from source2
    entries2 = [
        block for block in entries2
        if "[premier league]" in block[0].lower()
        or "[formula 1]" in block[0].lower()
        or "[england premier league]" in block[0].lower()
        or "[football]" in block[0].lower()
        or "[laliga]" in block[0].lower()
        or "[serie a]" in block[0].lower()
        or "[italy serie a]" in block[0].lower()       
    ]

    entries = entries1 + entries2  # merge both sources

    log_entries = [f"Run started at {datetime.now().isoformat()}"]
    print("Filtering...")
    filtered = [block for block in entries if is_block_allowed(block, log_entries)]

    # Separate TNT Sports channels
    tnt_blocks = []
    other_blocks = []
    for block in filtered:
        header = block[0].lower()
        if "tnt sports" in header:
            tnt_blocks.append(block)
        else:
            other_blocks.append(block)

    print(f"Total channels after filter: {len(filtered)}")
    print(f"TNT Sports channels prioritized: {len(tnt_blocks)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n")

        # Write TNT Sports first
        for block in tnt_blocks:
            for idx, line in enumerate(block):
                if idx == 0:
                    line = clean_extinf(line)
                else:
                    line = line.replace("|", "").replace(",,", ",")
                f.write(line + "\n")

        # Then write the rest
        for block in other_blocks:
            for idx, line in enumerate(block):
                if idx == 0:
                    line = clean_extinf(line)
                else:
                    line = line.replace("|", "").replace(",,", ",")
                f.write(line + "\n")

    # Write log file
    with open(LOG_FILE, "w", encoding="utf-8") as logf:
        for entry in log_entries:
            logf.write(entry + "\n")

    print(f"✅ Done: saved to {OUTPUT_FILE}, log written to {LOG_FILE}")

if __name__ == "__main__":
    main()
