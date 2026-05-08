#!/usr/bin/env bash

set -e

# Resolve script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$SCRIPT_DIR/data"
URLS_FILE="$SCRIPT_DIR/urls.txt"
COOKIES_FILE="$SCRIPT_DIR/cookies.txt"

mkdir -p "$DATA_DIR"
rm -rf "$DATA_DIR"/*

echo "==> Checking yt-dlp..."

if command -v yt-dlp >/dev/null 2>&1; then
    echo "yt-dlp found. Updating..."
    yt-dlp -U || true
else
    echo "yt-dlp not found. Installing latest version..."
    curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp \
        -o /usr/local/bin/yt-dlp
    chmod a+rx /usr/local/bin/yt-dlp
fi

echo "==> Checking ffmpeg..."

if ! command -v ffmpeg >/dev/null 2>&1; then
    echo "ffmpeg not found. Installing..."
    apt update
    apt install -y ffmpeg
else
    echo "ffmpeg already installed."
fi

echo "==> Starting download..."

if [[ ! -f "$URLS_FILE" ]]; then
    echo "ERROR: urls.txt not found!"
    exit 1
fi

YT_ARGS=(
    -a "$URLS_FILE"
    -P "$DATA_DIR"
    --no-playlist
    --ignore-errors
    --continue
    --no-overwrites
    --format "bv*[height<=720]+ba/best[height<=720]"
    --merge-output-format mp4
	--js-runtimes bun
)

# Add cookies if exists
if [[ -f "$COOKIES_FILE" ]]; then
    echo "Using cookies.txt"
    YT_ARGS+=(--cookies "$COOKIES_FILE")
fi

yt-dlp "${YT_ARGS[@]}"
python r1.py

echo "==> Done. Files saved in: $DATA_DIR"