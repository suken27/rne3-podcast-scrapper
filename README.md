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
python script.py [--config config.txt] [--dest path]
```

#### Options

- `--config FILE`: Config file with lines of 'URL latest_count' (default: /app/config.txt in container, config.txt locally)
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
docker run -v /host/path/to/downloads:/downloads -e DEFAULT_DEST=/downloads rtve-scraper
```

#### Custom Config File
Mount your own config file:
```bash
docker run -v /host/path/to/downloads:/downloads -v $(pwd)/myconfig.txt:/app/config.txt -e DEFAULT_DEST=/downloads rtve-scraper --config /app/config.txt
```

#### Scheduled Runs with Cron
Run with scheduling inside the container (uses the default config.txt):
```bash
docker run -d \
  -v /host/path/to/downloads:/downloads \
  -e CRON_EXPRESSION="0 */6 * * *" \
  -e DEFAULT_DEST=/downloads \
  rtve-scraper
```

**Environment Variables:**
- `CRON_EXPRESSION`: Cron expression for scheduling (e.g. `"0 */6 * * *"` for every 6 hours)
- `SLEEP_INTERVAL`: Ignored when cron is used; cron controls schedule

When `CRON_EXPRESSION` is set, the container starts cron and logs job output to container logs. Otherwise, it runs once and exits.

**Important:** The `--dest` path must be within a mounted volume to persist downloads outside the container. The `DEFAULT_DEST` environment variable is set to `/downloads` in the Docker Compose setup.

### Docker Compose Usage

Using Docker Compose provides a more convenient way to manage volumes and environment variables.

Create a `docker-compose.yml` file in your project directory:

```yaml
version: '3.8'

services:
  rtve-scraper:
    image: rtve-scraper  # or ghcr.io/yourusername/rne3-podcast-scrapper:latest
    container_name: rtve-scraper
    volumes:
      - ./downloads:/downloads  # Mount local downloads directory
      # Uncomment to override default config:
      # - ./config.txt:/app/config.txt
    environment:
      # Uncomment for scheduled runs:
      # CRON_EXPRESSION: "0 */6 * * *"  # Cron expression for every 6 hours
      # SLEEP_INTERVAL: 21600  # Sleep interval in seconds (default: 21600 = 6 hours)
    # For one-time run (default):
    command: ["--config", "/app/config.txt"]
    # For scheduled run, remove command and uncomment CRON_EXPRESSION
```

**Note:** Update the `image` to use the pre-built image or build locally with `docker-compose build`.

1. Create a local `downloads` directory:
   ```bash
   mkdir downloads
   ```

#### One-time Run with Docker Compose
```bash
docker-compose up
```

#### Scheduled Run with Docker Compose
Edit `docker-compose.yml` to uncomment `CRON_EXPRESSION` and set a cron expression, then run:
```bash
docker-compose up -d
```

The container will run continuously under cron, with logs visible via `docker-compose logs -f`.

#### Custom Config with Docker Compose
To use your own config file:
1. Create your `config.txt` in the project directory
2. Uncomment the config volume mount in `docker-compose.yml`:
   ```yaml
   volumes:
     - ./downloads:/downloads
     - ./config.txt:/app/config.txt
   ```
3. Run: `docker-compose up`

#### Environment Variables
- `CRON_EXPRESSION`: Cron expression for scheduling (e.g. `"0 */6 * * *"` for every 6 hours)
- `SLEEP_INTERVAL`: Ignored when cron is used; cron controls the schedule

When `CRON_EXPRESSION` is set, the container starts cron and logs output to the container logs. Otherwise, it runs once and exits.

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