import yt_dlp

url = input("Digite a URL do YouTube: ").strip()

opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

try:
    print("Baixando audio com yt-dlp...")
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
    print("Download de audio finalizado!")
except Exception as e:
    print(f"ERRO: {e}")
