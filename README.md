# 🎥 Youtube & TikTok Downloader UI (Flask)

A simple Flask-based web application to download YouTube, TikTok, or other videos.
Supports batch URL input, optional audio-only (MP3) conversion, and returns a ZIP archive of all downloaded files.

## ✨ Features

- Paste multiple URLs (one per line)
- Optional MP3 conversion (audio-only)
- Auto-zip all downloaded content
- Simple HTML form UI (Bootstrap-ready)
- Runs locally, no user data saved

## 📦 Installation

Install dependencies with:
```bash
python -m venv venv
venv\Scripts\activate
git clone https://github.com/adigayung/youtube-tiktok-downloader
cd youtube-tiktok-downloader
pip install -r requirements.txt
```
Content of requirements.txt:

Flask
yt-dlp

## 🚀 Running the App
```bash
python app.py
```

## 📝 Usage

1. Enter one or more YouTube/TikTok video URLs (one per line)
2. Check "Audio Only" if you want MP3 format
3. Click Download
4. You'll receive a .zip file containing all processed content

## 📂 Folder Structure

- app.py
- templates/
  - index.html
- downloads/
  - <UUID>/         ← downloaded files
  - <UUID>.zip      ← zipped output

## 📜 License

This project is licensed under the MIT License.
