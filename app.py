from flask import Flask, render_template, request, send_file, flash
import yt_dlp
import os
import shutil
import uuid
import sys

# ==================== Konfigurasi ====================
app = Flask(__name__)
app.secret_key = "super_secret_key"

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

My_Port = 7534
debug_mode = False
NGROK_AUTH_TOKEN = None  # default None

# ==================== Route ====================
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
                    print(f"Downloading: {url}")
                    ydl.download([url])

            zip_path = os.path.join(DOWNLOAD_FOLDER, f"{batch_id}.zip")
            shutil.make_archive(zip_path.replace(".zip", ""), 'zip', batch_folder)
            return send_file(zip_path, as_attachment=True)

        except Exception as e:
            flash(f"Gagal download: {str(e)}", "danger")

    return render_template("index.html")


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

    app.run(host="0.0.0.0", port=My_Port, debug=debug_mode)
