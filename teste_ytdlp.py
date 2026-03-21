import subprocess
import glob

url = input("Digite a URL do YouTube: ").strip()

try:
    print("Baixando legendas...")
    
    subprocess.run([
        "yt-dlp",
        "--write-auto-sub",
        "--sub-lang", "pt",
        "--skip-download",
        "-o", "resultado_ytdlp_temp",
        url
    ], check=True, text=True, encoding="utf-8", errors="replace", timeout=60)
    
    arquivos = glob.glob("resultado_ytdlp_temp.*")
    
    if arquivos:
        print(f"[OK] Legenda salva como: {arquivos[0]}")
    else:
        print("[AVISO] O yt-dlp nao encontrou nenhuma legenda.")
        
except Exception as e:
    print(f"[ERRO] no yt-dlp: {e}")
