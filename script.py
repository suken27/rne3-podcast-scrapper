#!/usr/bin/env python3
"""Download .mp3 files from the RTVE Turbo audio page with metadata."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TRCK, APIC, TCON, COMM
from mutagen.mp3 import MP3


def fetch_page(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return response.text


def sanitize_filename(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()


def parse_date_for_filename(date_text: str) -> str:
    # Assume DD/MM/YYYY format
    parts = date_text.split('/')
    if len(parts) == 3:
        try:
            day, month, year = map(int, parts)
            return f"{year:04d}_{month:02d}_{day:02d}"
        except ValueError:
            pass
    return "unknown_date"


def download_mp3(url: str, filepath: Path) -> bool:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Accept": "audio/mpeg,audio/*;q=0.9,*/*;q=0.8",
            "Referer": "https://www.rtve.es/play/audios/turbo-3/",
        }
        response = requests.get(url, headers=headers, stream=True, timeout=30, allow_redirects=True)
        response.raise_for_status()
        with filepath.open('wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False


def clean_cover_image_url(url: str) -> str:
    return url.split('?', 1)[0]


def download_image(url: str, filepath: Path) -> bool:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Accept": "image/*,*/*;q=0.8",
            "Referer": "https://www.rtve.es/play/audios/turbo-3/",
        }
        response = requests.get(clean_cover_image_url(url), headers=headers, timeout=30, allow_redirects=True)
        response.raise_for_status()
        filepath.write_bytes(response.content)
        return True
    except Exception as e:
        print(f"Error downloading image {url}: {e}")
        return False


def add_metadata(filepath: Path, title: str, artist: str, album: str, date: str, image_url: str = "", duration: str = "") -> None:
    try:
        audio = MP3(filepath, ID3=ID3)
        if audio.tags is None:
            audio.add_tags()
        audio.tags.add(TIT2(encoding=3, text=title))
        audio.tags.add(TPE1(encoding=3, text=artist))
        audio.tags.add(TALB(encoding=3, text=album))
        audio.tags.add(TCON(encoding=3, text="Podcast"))
        if duration:
            audio.tags.add(COMM(encoding=3, lang='eng', desc='Duration', text=duration))
        if date:
            # Parse date to YYYY-MM-DD
            try:
                parts = date.split('/')
                if len(parts) == 3:
                    day, month, year = map(int, parts)
                    iso_date = f"{year:04d}-{month:02d}-{day:02d}"
                    audio.tags.add(TDRC(encoding=3, text=iso_date))
            except ValueError:
                pass
        
        # Add cover image if available
        if image_url:
            try:
                response = requests.get(image_url, timeout=10)
                response.raise_for_status()
                image_data = response.content
                mime_type = response.headers.get('content-type', 'image/jpeg')
                if not mime_type.startswith('image/'):
                    mime_type = 'image/jpeg'
                audio.tags.add(APIC(encoding=3, mime=mime_type, type=3, desc='Cover', data=image_data))
                print(f"Cover image added from {image_url}")
            except Exception as e:
                print(f"Error downloading cover image from {image_url}: {e}")
        
        audio.save()
        print(f"Metadata added to {filepath}")
    except Exception as e:
        print(f"Error adding metadata to {filepath}: {e}")


def parse_audio_items(html_content: str, base_url: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html_content, "html.parser")
    items: list[dict[str, str]] = []
    seen_urls: set[str] = set()

    for li in soup.select("li.elem_"):
        item: dict[str, str] = {
            "date": "",
            "podcast_title": "",
            "episode_title": "",
            "mp3_url": "",
            "image_url": "",
            "duration": "",
        }

        share_tag = li.find(attrs={"data-share": True})
        data_setup = li.get("data-setup") or ""
        data_share = share_tag["data-share"] if share_tag else ""

        if data_share:
            try:
                data = json.loads(html.unescape(data_share))
            except json.JSONDecodeError:
                data = {}
            file_url = data.get("file", "")
            if file_url:
                item["mp3_url"] = urljoin(base_url, file_url)
            item["podcast_title"] = data.get("programTitle", "")
            item["episode_title"] = data.get("contentTitle", "")

        elif data_setup:
            try:
                data = json.loads(html.unescape(data_setup))
            except json.JSONDecodeError:
                data = {}
            item["episode_title"] = data.get("title", "")

        if not item["episode_title"]:
            title_tag = li.select_one(".maintitle")
            if title_tag:
                item["episode_title"] = title_tag.get_text(strip=True)

        if not item["podcast_title"]:
            program_tag = li.select_one(".program")
            if program_tag:
                item["podcast_title"] = program_tag.get_text(strip=True)

        date_tag = li.select_one(".datemi")
        if date_tag:
            item["date"] = date_tag.get_text(strip=True)

        duration_tag = li.select_one(".duration")
        if duration_tag:
            item["duration"] = duration_tag.get_text(strip=True)

        if not item["mp3_url"]:
            for match in re.findall(r'https?://[^"\'\s<>\&]+?\.mp3', str(li), flags=re.IGNORECASE):
                item["mp3_url"] = match
                break

        # Extract image URL
        img_tag = li.select_one("img.i_back")
        if img_tag:
            item["image_url"] = img_tag.get("src", "")

        if item["mp3_url"] and item["mp3_url"] not in seen_urls:
            seen_urls.add(item["mp3_url"])
            items.append(item)

    return items


def process_url(url: str, latest: int | None, dest: str) -> None:
    page_html = fetch_page(url)
    soup = BeautifulSoup(page_html, "html.parser")
    
    # Extract artist from character span
    artist_tag = soup.select_one(".character")
    page_artist = artist_tag.get_text(strip=True) if artist_tag else ""

    # Extract page-level cover image outside episode list
    page_cover_url = ""
    for img in soup.select("img.i_back"):
        if not img.find_parent("li", class_="elem_"):
            page_cover_url = img.get("src", "")
            break
    
    items = parse_audio_items(page_html, url)

    if latest is not None:
        items = items[: latest]

    if not items:
        print(f"No audio items found for {url}.")
        return

    # Group by podcast_title for folder creation
    podcast_folders: dict[str, list[dict[str, str]]] = {}
    for item in items:
        podcast = sanitize_filename(item.get("podcast_title", "Unknown_Podcast"))
        if podcast not in podcast_folders:
            podcast_folders[podcast] = []
        podcast_folders[podcast].append(item)

    for podcast, episodes in podcast_folders.items():
        folder = Path(dest) / podcast
        folder.mkdir(parents=True, exist_ok=True)

        cover_path = folder / "cover.jpg"
        if not cover_path.exists():
            cover_image_url = page_cover_url or next((item.get("image_url", "") for item in episodes if item.get("image_url")), "")
            if cover_image_url:
                if download_image(cover_image_url, cover_path):
                    print(f"Saved cover image to {cover_path}")
                else:
                    print(f"Failed to save cover image for {podcast}")

        for item in episodes:
            date_str = parse_date_for_filename(item.get("date", ""))
            filename = f"{date_str}.mp3"
            filepath = folder / filename

            mp3_url = item.get("mp3_url", "")
            if not mp3_url:
                print(f"Skipping {item.get('episode_title', 'Unknown')}: no MP3 URL")
                continue

            if filepath.exists():
                print(f"Skipping {filename}: already exists")
                continue

            print(f"Downloading {filename} to {folder}...")
            if download_mp3(mp3_url, filepath):
                # Add metadata
                title = item.get("episode_title", "")
                artist = page_artist or item.get("podcast_title", "")
                album = item.get("podcast_title", "")
                date = item.get("date", "")
                image_url = item.get("image_url", "")
                duration = item.get("duration", "")
                add_metadata(filepath, title, artist, album, date, image_url, duration)
                print(f"Downloaded and tagged {filepath}")
            else:
                print(f"Failed to download {filename}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Download .mp3 files from RTVE audio pages.")
    parser.add_argument(
        "--config",
        default="/app/config.txt",
        help="Config file with lines of 'URL latest_count' (default: /app/config.txt)",
    )
    parser.add_argument(
        "--dest",
        default=os.environ.get("DEFAULT_DEST", "."),
        help="Destination directory for downloads (default: current directory or DEFAULT_DEST env var)",
    )
    args = parser.parse_args()

    print(f"Configuration:")
    print(f"  Config file: {args.config}")
    print(f"  Destination: {args.dest}")

    with open(args.config, 'r') as f:
        configs = [line.strip().split() for line in f if line.strip()]
    
    print(f"  Sources ({len(configs)}):")
    for config in configs:
        if len(config) >= 2:
            url, latest = config[0], int(config[1])
            print(f"    {url} -> latest {latest} episodes")
        else:
            print(f"    Invalid line: {' '.join(config)}")
    
    print("Starting downloads...")

    for config in configs:
        if len(config) >= 2:
            url, latest = config[0], int(config[1])
            print(f"Processing {url} with latest {latest}")
            process_url(url, latest, args.dest)
        else:
            print(f"Invalid config line: {' '.join(config)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
