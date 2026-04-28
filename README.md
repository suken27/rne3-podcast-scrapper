# RTVE Podcast Scraper

A Python script to download MP3 files from RTVE audio pages, organizing them by podcast with proper metadata.

## Disclaimer

This repository has been generated entirely by generative LLM.

## Features

- Scrapes RTVE audio pages for MP3 links
- Downloads MP3 files to organized folders (podcast name)
- Names files with date format: `YYYY_MM_DD.mp3`
- Adds ID3 metadata: title, artist, album, date
- Skips existing files to avoid re-downloads
- Supports limiting to latest episodes
- Customizable download destination
- Docker support for containerized execution

## Requirements

- Python 3.8+
- Dependencies: `requests`, `beautifulsoup4`, `mutagen`

## Installation

### Local Installation

1. Clone or download the repository
2. Install dependencies:
   ```bash
   pip install requests beautifulsoup4 mutagen
   ```

### Docker Installation

1. Build the Docker image locally:
   ```bash
   docker build -t rtve-scraper .
   ```

2. Or use the pre-built image from GitHub Container Registry:
   ```bash
   docker pull ghcr.io/yourusername/rne3-podcast-scrapper:latest
   ```
   (Replace `yourusername` with your GitHub username)

### GitHub Actions

The repository includes a GitHub Actions workflow that automatically builds and pushes the Docker image to GitHub Container Registry on pushes to the main branch and on version tags.

To enable this:
1. Ensure your repository has GitHub Container Registry enabled (it's enabled by default for public repos)
2. The workflow will run automatically on pushes
3. Images will be available at `ghcr.io/yourusername/rne3-podcast-scrapper`

## Usage

### Local Usage

```bash
python script.py --config config.txt [--dest path]
```

#### Options

- `--config FILE`: Config file with lines of 'URL latest_count' (required)
- `--dest PATH`: Destination directory for downloads (default: current directory)

#### Examples

Use config file:
```bash
echo "https://www.rtve.es/play/audios/turbo-3/ 5" > config.txt
python script.py --config config.txt --dest ~/podcasts
```


### Docker Usage

Replace `rtve-scraper` with `ghcr.io/yourusername/rne3-podcast-scrapper:latest` in the examples below if using the pre-built image.

#### One-time Run
Run once using the default config:
```bash
docker run -v /host/path/to/downloads:/downloads rtve-scraper --config /app/config.txt
```

#### Custom Config File
Mount your own config file:
```bash
docker run -v /host/path/to/downloads:/downloads -v $(pwd)/myconfig.txt:/app/config.txt rtve-scraper --config /app/config.txt
```

#### Scheduled Runs with Cron
Run with cron scheduling inside the container (uses the default config.txt):
```bash
docker run -d \
  -v /host/path/to/downloads:/downloads \
  -e CRON_EXPRESSION="0 */6 * * *" \
  rtve-scraper
```

**Environment Variables:**
- `CRON_EXPRESSION`: Cron expression for scheduling (e.g., `"0 * * * *"` for hourly)

When `CRON_EXPRESSION` is set, the container runs cron and executes the script on schedule using the default config.txt. Otherwise, it runs once and exits.

**Important:** The `--dest` path must be within a mounted volume to persist downloads outside the container.

## Output Structure

Downloads are organized as:
```
<dest>/
├── <Podcast Name>/
│   ├── 2026_04_28.mp3
│   ├── 2026_04_27.mp3
│   └── ...
```

Each MP3 file includes metadata:
- Title: Episode title
- Artist: Podcast name
- Album: Podcast name
- Date: Episode date

## Notes

- The script respects RTVE's terms of service
- Downloads may fail if MP3 URLs require authentication or are geo-restricted
- Use responsibly and for personal use only

## License

[Add license if applicable]