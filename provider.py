import requests
import re
from datetime import datetime

SOURCE_URL = "https://raw.githubusercontent.com/raid35/docs/main/SPORT_UROP.m3u"
OUTPUT_FILE = "stv2.m3u"
LOG_FILE    = "stv2.log"

HEADER = '#EXTM3U x-tvg-url="https://bit.ly/3THSiiN"'

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
    # Ensure EXTINF has no attributes, just channel name
    if "," in line:
        channel_name = line.split(",", 1)[-1].strip()
        # Normalize capitalization (Title Case)
        channel_name = channel_name.title()
        line = f"#EXTINF:-1,{channel_name}"
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
    print("Downloading playlist...")
    source = download(SOURCE_URL)

    print("Parsing playlist...")
    entries = parse_m3u(source)

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
