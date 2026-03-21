import glob
import os
import subprocess

from out_dir import out_dir

url = input("Digite a URL do YouTube: ").strip()

try:
    print("Baixando legendas...")
    _out = out_dir()
    base = os.path.join(_out, "resultado_ytdlp_temp")
    subprocess.run([
        "yt-dlp",
        "--write-auto-sub",
        "--sub-lang", "pt",
        "--skip-download",
        "-o", base + ".%(ext)s",
        url
    ], check=True, text=True, encoding="utf-8", errors="replace", timeout=60)
    
    arquivos = glob.glob(os.path.join(_out, "resultado_ytdlp_temp.*"))
    
    if arquivos:
        print(f"[OK] Legenda salva como: {arquivos[0]}")
    else:
        print("[AVISO] O yt-dlp nao encontrou nenhuma legenda.")
        
except Exception as e:
    print(f"[ERRO] no yt-dlp: {e}")
