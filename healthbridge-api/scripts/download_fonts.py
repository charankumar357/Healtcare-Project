"""
Download Noto Sans fonts for Hindi/Telugu Unicode PDF rendering.
Run once: python scripts/download_fonts.py
"""

import os
import urllib.request

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts")

FONTS = {
    "NotoSans-Regular.ttf":
        "https://github.com/google/fonts/raw/main/ofl/notosans/NotoSans%5Bwdth%2Cwght%5D.ttf",
    "NotoSansDevanagari-Regular.ttf":
        "https://github.com/google/fonts/raw/main/ofl/notosansdevanagari/NotoSansDevanagari%5Bwdth%2Cwght%5D.ttf",
    "NotoSansTelugu-Regular.ttf":
        "https://github.com/google/fonts/raw/main/ofl/notosanstelugu/NotoSansTelugu%5Bwdth%2Cwght%5D.ttf",
}

def main():
    os.makedirs(FONT_DIR, exist_ok=True)
    for name, url in FONTS.items():
        dest = os.path.join(FONT_DIR, name)
        if os.path.exists(dest):
            print(f"  Already exists: {name}")
            continue
        print(f"  Downloading {name} ...")
        try:
            urllib.request.urlretrieve(url, dest)
            size_kb = os.path.getsize(dest) / 1024
            print(f"  Saved: {name} ({size_kb:.0f} KB)")
        except Exception as e:
            print(f"  FAILED: {name} — {e}")
            print(f"  You can manually download Noto Sans from https://fonts.google.com/noto")

    print(f"\nFont directory: {FONT_DIR}")
    print("Fonts are needed for Hindi/Telugu PDF support.")


if __name__ == "__main__":
    main()
