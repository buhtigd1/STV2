import requests
import re

SOURCE_URL = "https://raw.githubusercontent.com/raid35/docs/main/SPORT_UROP.m3u"
OUTPUT_FILE = "stv2.m3u"

HEADER = '#EXTM3U url-tvg="https://bit.ly/3THSiiN"'

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
    # Remove group-title and any "|" characters
    line = re.sub(r'\s*group-title="[^"]+"', '', line, flags=re.IGNORECASE)
    line = line.replace("|", "")
    line = line.replace(",,", ",")
    return line

def clean_line(line):
    # General cleanup for non-EXTINF lines
    line = line.replace("|", "")
    line = line.replace(",,", ",")
    return line

def is_block_allowed(block):
    """Skip CAZE TV 1 and CAZE TV 2"""
    if not block:
        return False
    header = block[0].lower()
    if "caze tv 1" in header or "caze tv 2" in header:
        return False
    return True

def main():
    print("Downloading playlist...")
    source = download(SOURCE_URL)

    print("Parsing playlist...")
    entries = parse_m3u(source)

    print("Filtering...")
    filtered = [block for block in entries if is_block_allowed(block)]

    print(f"Total channels after filter: {len(filtered)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n")
        for block in filtered:
            for idx, line in enumerate(block):
                if idx == 0:  # EXTINF line
                    line = clean_extinf(line)
                else:         # URL or other lines
                    line = clean_line(line)
                f.write(line + "\n")

    print(f"✅ Done: saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
