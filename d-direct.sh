#!/usr/bin/env bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$SCRIPT_DIR/data"
DIRECT_URLS_FILE="$SCRIPT_DIR/direct_urls.txt"

mkdir -p "$DATA_DIR"

echo "==> Starting direct file download..."
echo "==> Working directory: $DATA_DIR"

if [[ ! -f "$DIRECT_URLS_FILE" ]]; then
    echo "ERROR: direct_urls.txt not found!"
    exit 1
fi

echo "==> Reading URLs from file..."

# Read all URLs into array
urls=()
while IFS= read -r line || [[ -n "$line" ]]; do
    url=$(echo "$line" | xargs)
    if [[ -n "$url" ]]; then
        urls+=("$url")
        echo "Found URL: $url"
    fi
done < "$DIRECT_URLS_FILE"

echo "==> Total URLs to process: ${#urls[@]}"

if [[ ${#urls[@]} -eq 0 ]]; then
    echo "ERROR: No valid URLs found"
    exit 1
fi

successful=0
failed=0

# Process each URL
for url in "${urls[@]}"; do
    echo ""
    echo "==> Downloading: $url"
    
    # Extract filename
    filename=$(basename "$url" | cut -d '?' -f1 | cut -d '#' -f1)
    if [[ -z "$filename" ]]; then
        filename="file_$(date +%s)"
    fi
    
    output_path="$DATA_DIR/$filename"
    echo "==> Saving to: $output_path"
    
    # Download the file
    if curl -L --fail --max-time 300 -o "$output_path" "$url" 2>/dev/null; then
        if [[ -f "$output_path" ]]; then
            echo "✅ SUCCESS: Downloaded $filename"
            successful=$((successful + 1))
        else
            echo "❌ FAILED: File not created"
            failed=$((failed + 1))
        fi
    else
        echo "❌ FAILED: curl error for $url"
        failed=$((failed + 1))
    fi
done

echo ""
echo "========================================="
echo "DOWNLOAD SUMMARY"
echo "Successful: $successful"
echo "Failed: $failed"
echo "========================================="

echo ""
echo "Files in data directory:"
ls -la "$DATA_DIR"

if [[ $successful -gt 0 ]]; then
    echo ""
    echo "==> Uploading to Rubika..."
    python /app/r1.py
    echo "==> Upload completed"
else
    echo "==> No files to upload"
    exit 1
fi

echo ""
echo "==> Job completed successfully"
exit 0