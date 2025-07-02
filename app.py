from flask import stream_with_context, Response, Flask, render_template, request, send_file, flash
import queue
import yt_dlp
import webview
import threading
import os
import shutil
import uuid
import sys

# ==================== Konfigurasi ====================
app = Flask(__name__)
log_queue = queue.Queue()
app.secret_key = "super_secret_key"

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

My_Port = 7534
debug_mode = False
NGROK_AUTH_TOKEN = None  # default None

def log_print(text):
    print(text)
    log_queue.put(text)
    
def thread_download(urls, sound_only, batch_id):
    batch_folder = os.path.join(DOWNLOAD_FOLDER, batch_id)
    os.makedirs(batch_folder, exist_ok=True)

    ydl_opts = {
        'outtmpl': os.path.join(batch_folder, '%(title)s.%(ext)s'),
        'format': 'bestaudio/best' if sound_only else 'bestvideo+bestaudio/best',
    }

    if sound_only:
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for url in urls:
                log_print(f"🔗 Downloading: {url}")
                ydl.download([url])

        zip_path = os.path.join(DOWNLOAD_FOLDER, f"{batch_id}.zip")
        shutil.make_archive(zip_path.replace(".zip", ""), 'zip', batch_folder)
        log_print(f"✅ Selesai. File ZIP: {zip_path}")

    except Exception as e:
        log_print(f"❌ Error: {str(e)}")


# ==================== Route ====================
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

        # ⬇️ Pindahkan proses download ke thread
        threading.Thread(target=thread_download, args=(urls, sound_only, batch_id), daemon=True).start()

        # ⬇️ Langsung render log.html
        return render_template("log.html")

    return render_template("index.html")

def running_in_colab():
    try:
        import google.colab
        return True
    except ImportError:
        return False
        
def run_flask():
    app.run(host="0.0.0.0", port=My_Port, debug=debug_mode)
# ==================== Main ====================
if __name__ == "__main__":
    # Ambil token dari argumen (jika ada)
    if any("--NGROK_AUTH_TOKEN" in arg for arg in sys.argv):
        import argparse
        from pyngrok import ngrok, conf

        parser = argparse.ArgumentParser()
        parser.add_argument("--NGROK_AUTH_TOKEN", type=str, default=None)
        args = parser.parse_args()
        NGROK_AUTH_TOKEN = args.NGROK_AUTH_TOKEN

        if NGROK_AUTH_TOKEN:
            conf.get_default().auth_token = NGROK_AUTH_TOKEN
            public_url = ngrok.connect(My_Port)
            print("🌐 Public URL:", public_url)

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Jalankan webview jika bukan di Colab
    if not running_in_colab():
        webview.create_window("🎧 Batch YouTube & Tiktok Downloader", f"http://127.0.0.1:{My_Port}/")
        webview.start()
    else:
        print("💡 Deteksi: Anda menjalankan kode di Google Colab. pywebview tidak dijalankan.")