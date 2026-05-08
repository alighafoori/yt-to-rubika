```markdown
# 🎬 YouTube & Direct Downloader to Rubika

A web-based tool to download videos from YouTube (using `yt-dlp`) and files from direct URLs (using `curl`), then automatically upload them to your Rubika account.

## ✨ Features

- **YouTube Downloader**: Download videos (720p max with audio, MP4 format)
- **Direct File Downloader**: Download any file type (PDF, ZIP, MP4, images, etc.) from direct URLs
- **Web Interface**: Clean, responsive UI with live logging
- **Docker Support**: Easy deployment with Docker Compose
- **Automatic Upload**: Files are automatically uploaded to your Rubika account
- **Session Persistence**: Rubika login session saved for repeated use

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- A Rubika account

### 1. Clone the Repository

```bash
git clone https://github.com/alighafoori/yt-to-rubika.git
cd yt-to-rubika
```

### 2. Set Up Rubika Authentication

You need to generate a Rubika session file **before** running the container:

```bash
# Install required Python packages
pip install rubpy python-dotenv

# Create a .env file (optional, default session name is "rubika_session")
echo "RUBIKA_SESSION=rubika_session" > .env

# Run the login script
python rubika-login.py
```

**Login Process:**
1. You'll be prompted to enter your phone number (with country code, e.g., `+989123456789`)
2. Rubika will send a verification code to your number
3. Enter the verification code when prompted
4. A `rubika_session.rp` file will be created in the current directory

> **Note:** The session file keeps you logged in. Keep it secure and never commit it to version control.

### 3. Configure Docker Compose

Edit `docker-compose.yml`:

- **Change the image path** (line 5) to your own repository:
  ```yaml
  image: ghcr.io/YOUR_USERNAME/yt-to-rubika/yt-to-rubika:latest
  ```

- **Mount your session file** (already configured):
  ```yaml
  volumes:
    - ./data:/app/data
    - ./rubika_session.rp:/app/rubika_session.rp:ro
  ```

- **Optional**: Uncomment and configure Traefik labels if using Traefik as reverse proxy

### 4. Build and Run

```bash
# Build the Docker image
docker compose build

# Run the container
docker compose up -d
```

The web interface will be available at `http://localhost:5000`

### 5. Using the Web Interface

#### 🎬 Downloading YouTube Videos

1. Switch to the **"YouTube Downloader"** tab
2. Enter one YouTube URL per line (supports both `youtube.com` and `youtu.be`)
3. **Optional**: Provide cookies for age-restricted videos or private playlists (Netscape format)
4. Click **"Start Download & Upload"**

#### 📎 Downloading Direct Files

1. Switch to the **"Direct File Download"** tab
2. Enter one direct file URL per line
3. Click **"Start Download & Upload"**

The live log pane will show real-time progress. All downloaded files are automatically uploaded to your Rubika account (sent to "Saved Messages").

## 🍪 Getting YouTube Cookies (Netscape Format)

For age-restricted videos or to access private content, you need to provide cookies:

### Using Browser Extensions

**Chrome/Edge:**
1. Install [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
2. Log into YouTube in your browser
3. Click the extension icon and select "Export"
4. Copy the cookies.txt content

**Firefox:**
1. Install [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)
2. Log into YouTube
3. Click the extension icon and export cookies
4. Copy the content

**Manual Method (Advanced):**
1. Log into YouTube in a private/incognito window
2. Open Developer Tools (F12) → Application/Storage → Cookies
3. Export using browser tools or use a script

> ⚠️ **Security Warning**: Cookies contain your login session. Never share them or commit them to version control. Use them only for your own private YouTube access.

## 🛠 Architecture

```
User → Flask Web UI (port 5000)
          ↓
    [Choose job type]
          ↓
    YouTube Job          Direct Job
    (d.sh)              (d-direct.sh)
          ↓                  ↓
    yt-dlp              curl
    downloads           downloads
          ↓                  ↓
    r1.py (Rubika uploader)
          ↓
    Rubika account
```

## 📁 File Structure

```
yt-to-rubika/
├── app.py                 # Flask web application
├── d.sh                   # YouTube download script
├── d-direct.sh            # Direct file download script
├── r1.py                  # Rubika uploader
├── rubika-login.py        # Session creation script
├── requirements.txt       # Python dependencies
├── dockerfile            # Docker build instructions
├── docker-compose.yml    # Docker Compose configuration
├── .github/workflows/    # GitHub Actions CI/CD
│   └── build.yml         # Automated Docker build
└── templates/
    └── index.html        # Web UI template
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file (optional):

```env
RUBIKA_SESSION=rubika_session  # Name of the session file
```

### Docker Volumes

- `./data:/app/data` - Downloaded files storage
- `./rubika_session.rp:/app/rubika_session.rp:ro` - Rubika session (read-only)

## 🛑 Stopping the Service

```bash
# Stop the container
docker compose down

# Stop and remove volumes (deletes downloaded files)
docker compose down -v
```

## 🔄 Updating

```bash
git pull
docker compose build
docker compose up -d
```

## 🐛 Troubleshooting

### "Rubika session not found"
- Run `python rubika-login.py` to create the session file
- Ensure `rubika_session.rp` is in the same directory as `docker-compose.yml`
- Check the volume mount path in `docker-compose.yml`

### "Job failed with exit code"
- Check the live logs for specific error messages
- For YouTube: Verify the URLs are valid and not age-restricted (or add cookies)
- For direct downloads: Ensure URLs are directly accessible (not behind redirects)

### "Cannot connect to Docker daemon"
- Ensure Docker is running: `sudo systemctl start docker` (Linux)
- On Windows/macOS, start Docker Desktop

### Port 5000 already in use
- Change the port in `docker-compose.yml`:
  ```yaml
  ports:
    - "5001:5000"  # Use port 5001 on host
  ```

## 📝 Notes

- YouTube videos are limited to **720p** with audio (MP4 format)
- Downloaded files are **automatically deleted** from the container after successful upload
- The web interface keeps the last **2000 log lines** for display
- Session file is mounted as read-only for security
- Direct downloads have a **5-minute timeout** per file

## 🛡 Security Recommendations

1. **Never commit** `rubika_session.rp`, `cookies.txt`, or `.env` to Git
2. Use `.gitignore` to exclude sensitive files
3. Run behind a reverse proxy (Traefik/Nginx) with HTTPS for production
4. Add authentication middleware if exposing to the internet
5. Regularly rotate Rubika session if compromised

## 📄 License

This project is open-source. Use at your own risk.

## 🤝 Contributing

Feel free to open issues or submit pull requests for improvements.

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloading
- [rubpy](https://github.com/AliMD/rubpy) - Rubika API client
- [Flask](https://flask.palletsprojects.com/) - Web framework
