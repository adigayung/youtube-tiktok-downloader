from flask import stream_with_context, Response, Flask, render_template, request, send_file, flash
import queue
import yt_dlp
import threading
import os
import shutil
import uuid
import sys
import time

# Optional: only import pywebview if not in Colab
try:
    import webview
except ImportError:
    webview = None  # handle safely later if in Colab

# ==================== Konfigurasi ====================
app = Flask(__name__)
log_queue = queue.Queue()
PUBLIC_URL = None
app.secret_key = "super_secret_key"

DOWNLOAD_FOLDER = "downloads"
OPEN_WEBVIEW = False
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

My_Port = 7534
debug_mode = False
NGROK_AUTH_TOKEN = None  # default None

# ==================== Utility ====================
def running_in_colab():
    try:
        import google.colab
        return True
    except ImportError:
        return False

def log_print(text):
    print(text)
    log_queue.put(text)

def format_size(bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"

def thread_download(urls, sound_only, batch_id):
    batch_folder = os.path.join(DOWNLOAD_FOLDER, batch_id)
    os.makedirs(batch_folder, exist_ok=True)

    ydl_opts = {
        'outtmpl': os.path.join(batch_folder, '%(title)s.%(ext)s'),
        'format': 'bestaudio/best' if sound_only else 'bestvideo+bestaudio/best',
        'quiet': True,
        'no_warnings': True,
    }

    if sound_only:
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    total_videos = len(urls)
    downloaded_bytes = 0
    start_time = time.time()

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for idx, url in enumerate(urls, start=1):
                log_print(f"\n📥 [{idx}/{total_videos}] Downloading: {url}")

                file_before = set(os.listdir(batch_folder))
                download_start = time.time()
                ydl.download([url])
                download_end = time.time()

                file_after = set(os.listdir(batch_folder))
                new_files = file_after - file_before
                new_bytes = 0
                for f in new_files:
                    path = os.path.join(batch_folder, f)
                    if os.path.isfile(path):
                        new_bytes += os.path.getsize(path)

                downloaded_bytes += new_bytes

                elapsed = time.time() - start_time
                avg_time = elapsed / idx
                eta = (total_videos - idx) * avg_time

                log_print(
                    f"✅ Done {idx}/{total_videos} | ETA: {eta:.1f}s | Total: {format_size(downloaded_bytes)} | Time: {download_end - download_start:.1f}s"
                )

        zip_path = os.path.join(DOWNLOAD_FOLDER, f"{batch_id}.zip")
        file_name = f"{batch_id}.zip"
        shutil.make_archive(zip_path.replace(".zip", ""), 'zip', batch_folder)

        if running_in_colab() and PUBLIC_URL:
            url_base = PUBLIC_URL
        else:
            url_base = f"http://127.0.0.1:{My_Port}"
        download_url = f"{url_base}/download/{file_name}"

        total_time = time.time() - start_time
        log_print(f"\n📦 Archive created: {file_name}")
        log_print(f"🕒 Total time: {total_time:.2f} seconds")
        log_print(f"📎 File size: {format_size(os.path.getsize(zip_path))}")
        log_print(f"🔗 <a href='{download_url}' download>{download_url}</a>")
        log_print(f"✅ Semua download selesai.")

    except Exception as e:
        log_print(f"❌ Error saat download: {str(e)}")

# ==================== Route ====================
@app.route("/download/<path:filename>")
def download_file(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File tidak ditemukan.", 404

@app.route("/log_stream")
def log_stream():
    def generate():
        while True:
            msg = log_queue.get()
            yield f"data: {msg}\n\n"
    return Response(stream_with_context(generate()), mimetype="text/event-stream")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        urls_text = request.form.get("youtube_urls", "").strip()
        sound_only = request.form.get("sound_only") == "on"

        if not urls_text:
            flash("Masukkan setidaknya satu URL.", "warning")
            return render_template("index.html")

        urls = [line.strip() for line in urls_text.splitlines() if line.strip()]
        if not urls:
            flash("Tidak ada URL valid ditemukan.", "danger")
            return render_template("index.html")

        batch_id = str(uuid.uuid4())
        threading.Thread(target=thread_download, args=(urls, sound_only, batch_id), daemon=True).start()

        return render_template("log.html")

    return render_template("index.html")

def run_flask():
    app.run(host="0.0.0.0", port=My_Port, debug=debug_mode)

# ==================== Start Server Function ====================
def start_server():
    global NGROK_AUTH_TOKEN

    if any("--NGROK_AUTH_TOKEN" in arg for arg in sys.argv):
        import argparse
        from pyngrok import ngrok, conf

        parser = argparse.ArgumentParser()
        parser.add_argument("--NGROK_AUTH_TOKEN", type=str, default=None)
        args = parser.parse_args()
        NGROK_AUTH_TOKEN = args.NGROK_AUTH_TOKEN

        if NGROK_AUTH_TOKEN:
            global PUBLIC_URL
            conf.get_default().auth_token = NGROK_AUTH_TOKEN
            PUBLIC_URL = str(ngrok.connect(My_Port))
            print("🌐 Public URL:", PUBLIC_URL)

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    if not OPEN_WEBVIEW:
        print("💡 Deteksi: Anda menjalankan kode di Google Colab. pywebview tidak dijalankan.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("⛔ Dihentikan oleh user")
    else:
        if running_in_colab():
            print("💡 Deteksi: Anda menjalankan kode di Google Colab. pywebview tidak dijalankan.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("⛔ Dihentikan oleh user")
        else:
            if webview is not None:
                webview.create_window("🎧 Batch YouTube & Tiktok Downloader", f"http://127.0.0.1:{My_Port}/")
                webview.start()
            else:
                print("⚠️ pywebview tidak tersedia.")

# ==================== MAIN ====================
if __name__ == "__main__":
    start_server()
