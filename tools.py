import os
import re
import subprocess
import sys
from pytubefix import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def get_video_id(url):
    match = re.search(r'(?:v=|\/|embed\/|shorts\/|be\/)([0-9A-Za-z_-]{11})', url)
    return match.group(1) if match else None

def save_to_file(filename, text):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"[OK] Arquivo salvo: {os.path.basename(filename)}")

def limpar_legenda(texto):
    linhas_limpas = []
    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha or linha.isdigit() or '-->' in linha:
            continue
        linha = re.sub(r'<[^>]+>', '', linha)
        if linha and (not linhas_limpas or linha != linhas_limpas[-1]):
            linhas_limpas.append(linha)
    return " ".join(linhas_limpas).strip()

def get_transcript_ytapi(video_id, folder):
    print("\n[1/3] youtube-transcript-api...")
    try:
        transcript = None
        for lang in [['pt'], ['pt-BR'], ['pt', 'pt-BR'], ['en']]:
            try:
                transcript = YouTubeTranscriptApi.list_transcripts(video_id).find_transcript(lang).fetch()
                break
            except:
                continue
        
        if not transcript:
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                for t in transcript_list:
                    transcript = t.fetch()
                    break
            except:
                pass

        if transcript:
            final_text = " ".join([entry.get('text', '') for entry in transcript]).strip()
            if final_text:
                save_to_file(os.path.join(folder, "transcricao_yt_api.txt"), final_text)
                return
        print("[AVISO] Nenhuma transcricao encontrada.")
    except Exception as e:
        print(f"[ERRO] {str(e)}")

def get_transcript_pytubefix(url, folder):
    print("\n[2/3] pytubefix...")
    try:
        yt = YouTube(url)
        caption = None
        for code in ['pt', 'pt-BR', 'a.pt', 'a.pt-BR', 'en', 'a.en']:
            if code in yt.captions:
                caption = yt.captions[code]
                break
        
        if not caption and yt.captions:
            caption = list(yt.captions.values())[0]

        if caption:
            final_text = limpar_legenda(caption.generate_srt_captions())
            if final_text:
                save_to_file(os.path.join(folder, "transcricao_pytubefix.txt"), final_text)
            else:
                print("[ERRO] Transcricao vazia.")
        else:
            print("[ERRO] Nenhuma legenda encontrada.")
    except Exception as e:
        print(f"[ERRO] {str(e)}")

def get_transcript_ytdlp(url, folder):
    print("\n[3/3] yt-dlp...")
    try:
        video_id = get_video_id(url)
        sub_file_base = os.path.join(folder, f"_sub_temp_{video_id}")
        
        subprocess.run([
            "yt-dlp", "--write-auto-sub", "--sub-lang", "pt", "--sub-format", "srt",
            "--skip-download", "--no-warnings", "-o", sub_file_base + ".%(ext)s", url
        ], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
        
        found_path = next((os.path.join(folder, f) for f in os.listdir(folder) if f.startswith(f"_sub_temp_{video_id}") and f.endswith(('.srt', '.vtt'))), None)
        
        if found_path:
            with open(found_path, "r", encoding="utf-8", errors="replace") as arq:
                final_text = limpar_legenda(arq.read())
            
            if final_text:save_to_file(os.path.join(folder, "transcricao_ytdlp.txt"), final_text)
            else: print("[ERRO] Legenda vazia.")
            
            os.remove(found_path)
        else:
            print("[ERRO] Nenhum arquivo baixado.")
    except Exception as e:
        print(f"[ERRO] {str(e)}")

def download_media(url, folder, mode='video'):
    print(f"\n[INICIO] Download de {mode}...")
    try:
        opts = {
            'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
            'quiet': True, 'no_warnings': True
        }
        if mode == 'audio':
            opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
            })
        else:
            opts.update({'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'})

        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        print(f"[OK] Download finalizado!")
    except Exception as e:
        print(f"[ERRO] {e}")

def main():
    print("="*40 + "\n      YOUTUBE TOOL - TRANSCRIPT & DOWNLOAD\n" + "="*40)
    
    url = input("\nDigite o link do vídeo do YouTube: ").strip()
    video_id = get_video_id(url) if url else None

    if not video_id:
        print("[ERRO] Link inválido ou vazio!")
        return

    folder = os.path.dirname(os.path.abspath(__file__))

    while True:
        print("\nO que você deseja fazer?\n1. Gerar Transcrições (3 métodos)\n2. Baixar VIDEO (MP4)\n3. Baixar AUDIO (MP3)\n0. Sair")
        choice = input("\nEscolha: ").strip()
        
        if choice == '1':
            get_transcript_ytapi(video_id, folder)
            get_transcript_pytubefix(url, folder)
            get_transcript_ytdlp(url, folder)
        elif choice == '2': download_media(url, folder, 'video')
        elif choice == '3': download_media(url, folder, 'audio')
        elif choice == '0': break
        else: print("[AVISO] Inválido.")

if __name__ == "__main__":
    main()
