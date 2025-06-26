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

## ☁️ Running the App on Google Colab

You can run this downloader app directly on Google Colab.  
Just click the link below to open the notebook:

👉[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://github.com/adigayung/youtube-tiktok-downloader/blob/main/colab.ipynb)

### 🔐 Ngrok Auth Token Required

To expose your app to the internet (using ngrok), you need an **Ngrok Authtoken**.

#### 🔽 Steps to Get Ngrok Authtoken:

1. Register or log in to Ngrok:  
   👉 https://dashboard.ngrok.com/signup

2. After logging in, go to your authtoken page:  
   👉 https://dashboard.ngrok.com/get-started/your-authtoken

3. Copy your token and run the app like this:

```bash
!python3 app.py --NGROK_AUTH_TOKEN=your_ngrok_api_token_here
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
