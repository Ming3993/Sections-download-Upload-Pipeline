import re
import subprocess
from uploader import upload_file

def extract_youtube_id(url):
    # regex pattern for popular link types
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})(?:\?|&|\/|$)"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def pipeline(filepath,access_token,item_id):
    with open(filepath, "r") as fin:
        i = 0
        link = ""
        for line in fin:
            if i % 2:
                intervals = re.split(r"[^\d]*;[^\d]*", line)

                for interval in intervals:
                    pivot = re.split(r"[^\d:]+", interval)

                    if len(pivot) == 3:
                        pivot.pop(-1)

                    start = re.split(":", pivot[0])
                    end = re.split(":", pivot[1])

                    start_str = ":".join(f"{int(n):02}" for n in start)
                    end_str = ":".join(f"{int(n):02}" for n in end)

                    download_sections = f"*{start_str}-{end_str}"
                    output_template = f"%(title)s_{start_str.replace(':','')}-{end_str.replace(':','')}.%(ext)s"

                    # yt-dlp command
                    cmd = [
                        "yt-dlp",
                        "--cookies", "cookies.txt",
                        "-f", "(bv*[vcodec~='^((he|a)vc|h26[45])']) / (bv*/b)",
                        "--download-sections", download_sections,
                        "--concurrent-fragments", "3",
                        "-o", output_template,
                        link.strip()
                    ]
                    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
                    
                    print("STDOUT:", result.stdout)
                    print("STDERR:", result.stderr)
                    print("Return code:", result.returncode)
                    if result.returncode == 0:
                        upload_file(item_id,access_token)
            else:
                link_id = extract_youtube_id(line)
                if link_id is not None:
                    link = f"https://www.youtube.com/watch?v={link_id}"
                else:
                    link = line

            i ^= 1