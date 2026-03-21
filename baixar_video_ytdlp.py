import os

import yt_dlp

from out_dir import out_dir

url = input("Digite a URL do YouTube: ").strip()

_out = out_dir()
opts = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'outtmpl': os.path.join(_out, '%(title)s.%(ext)s'),
}

try:
    print("Baixando video com yt-dlp...")
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
    print("Download de video finalizado!")
except Exception as e:
    print(f"ERRO: {e}")
