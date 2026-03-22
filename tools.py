import os
import re
import subprocess
import sys
import unicodedata
from datetime import datetime
from pytubefix import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp

from out_dir import out_dir

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def get_video_id(url):
    match = re.search(r'(?:v=|\/|embed\/|shorts\/|be\/)([0-9A-Za-z_-]{11})', url)
    return match.group(1) if match else None

def slugify_title(text, max_len=120):
    """Nome de arquivo seguro: minúsculas, hífens, sem acentos."""
    if not text or not str(text).strip():
        return ""
    s = unicodedata.normalize("NFKD", str(text))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    if not s:
        return ""
    return s[:max_len]

def fetch_video_metadata(url):
    """Metadados do vídeo/canal via yt-dlp (um único extract_info)."""
    opts = {"quiet": True, "no_warnings": True, "skip_download": True, "noplaylist": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
    if not info:
        return {}
    lang = info.get("language") or info.get("audio_language") or ""
    if isinstance(lang, list):
        lang = ", ".join(str(x) for x in lang)
    cats = info.get("categories")
    if isinstance(cats, list):
        cats_str = ", ".join(str(c) for c in cats)
    else:
        cats_str = (cats or "") or ""
    return {
        "title": (info.get("title") or info.get("id") or "").strip(),
        "id": (info.get("id") or "").strip(),
        "channel": (info.get("channel") or info.get("uploader") or "").strip(),
        "channel_id": (info.get("channel_id") or info.get("uploader_id") or "").strip(),
        "channel_url": (info.get("channel_url") or info.get("uploader_url") or "").strip(),
        "description": (info.get("description") or "").strip(),
        "duration": info.get("duration"),
        "view_count": info.get("view_count"),
        "upload_date": (info.get("upload_date") or "").strip(),
        "language_audio": str(lang).strip(),
        "categories": cats_str,
    }

def fetch_video_title(url):
    return (fetch_video_metadata(url).get("title") or "").strip()

def save_to_file(filename, text):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"[OK] Arquivo salvo: {os.path.basename(filename)}")

def _fmt_duration_sec(seconds):
    if seconds is None:
        return ""
    try:
        s = int(seconds)
        h, rem = divmod(s, 3600)
        m, sec = divmod(rem, 60)
        if h:
            return f"{h}:{m:02d}:{sec:02d}"
        return f"{m}:{sec:02d}"
    except (TypeError, ValueError):
        return str(seconds)

def _fmt_upload_date_yyyymmdd(ymd):
    if not ymd or len(str(ymd)) != 8:
        return str(ymd) if ymd else ""
    ymd = str(ymd)
    return f"{ymd[6:8]}/{ymd[4:6]}/{ymd[0:4]}"

def _md_escape_line(s, max_desc=1200):
    if not s:
        return ""
    s = s.strip()
    if len(s) > max_desc:
        s = s[: max_desc - 3].rstrip() + "..."
    return s

def format_transcript_markdown(video_title, url, body, metadata, transcript_language):
    """Markdown com título, link, blocos canal/vídeo/idioma, conteúdo e rodapé."""
    title_line = (video_title or "").strip() or "Sem título"
    meta = metadata or {}
    link_line = f"**Link:** {url.strip()}"

    ch_name = meta.get("channel") or "—"
    ch_id = meta.get("channel_id") or "—"
    ch_u = meta.get("channel_url") or "—"
    blo_canal = (
        "### Canal\n\n"
        f"- **Nome:** {ch_name}\n"
        f"- **ID:** {ch_id}\n"
        f"- **URL:** {ch_u}\n"
    )

    vid = meta.get("id") or "—"
    dur = _fmt_duration_sec(meta.get("duration")) or "—"
    views = meta.get("view_count")
    views_s = str(views) if views is not None else "—"
    pub = _fmt_upload_date_yyyymmdd(meta.get("upload_date")) or "—"
    cats = meta.get("categories") or "—"
    lang_audio = meta.get("language_audio") or "—"
    desc = _md_escape_line(meta.get("description") or "")

    blo_video = (
        "### Vídeo\n\n"
        f"- **ID:** `{vid}`\n"
        f"- **Duração:** {dur}\n"
        f"- **Visualizações:** {views_s}\n"
        f"- **Data de publicação:** {pub}\n"
        f"- **Categorias:** {cats}\n"
        f"- **Idioma (áudio informado pelo YouTube):** {lang_audio}\n"
    )
    if desc:
        blo_video += f"\n**Descrição (trecho):**\n\n> {desc.replace(chr(10), ' ')}\n"
    else:
        blo_video += "\n**Descrição:** —\n"

    lang_tr = (transcript_language or "").strip() or "—"
    blo_idioma = f"### Idioma da transcrição\n\n- **Legenda / transcrição usada:** {lang_tr}\n"

    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    rodape = f"\n---\n\n*Transcrito em: {agora}*"
    bloco = (body or "").strip()

    return (
        f"{title_line}\n\n{link_line}\n\n{blo_canal}\n{blo_video}\n{blo_idioma}\n"
        f"### Conteúdo\n\n{bloco}{rodape}"
    )

def save_transcript_output(filename, body, ext, url, video_title, metadata=None, transcript_language=None):
    ext = normalize_output_ext(ext)
    if ext == ".md":
        text = format_transcript_markdown(
            video_title, url, body, metadata or {}, transcript_language or "",
        )
    else:
        text = body
    save_to_file(filename, text)

def normalize_output_ext(ext):
    """Aceita 'txt', '.txt', 'md', '.md' → '.txt' ou '.md'."""
    if not ext:
        return ".txt"
    e = str(ext).strip().lower()
    if not e.startswith("."):
        e = "." + e
    return ".md" if e == ".md" else ".txt"

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

def get_transcript_ytapi(video_id, folder, slug, ext, url, video_title, metadata):
    print("\n[1/3] youtube-transcript-api...")
    try:
        transcript = None
        t_obj = None
        for lang in [['pt'], ['pt-BR'], ['pt', 'pt-BR'], ['en']]:
            try:
                t_obj = YouTubeTranscriptApi.list_transcripts(video_id).find_transcript(lang)
                transcript = t_obj.fetch()
                break
            except Exception:
                continue

        if not transcript:
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                for t_obj in transcript_list:
                    transcript = t_obj.fetch()
                    break
            except Exception:
                pass

        lang_label = ""
        if t_obj is not None:
            lang_label = f"{getattr(t_obj, 'language', '')} ({getattr(t_obj, 'language_code', '')})".strip()

        if transcript:
            final_text = " ".join([entry.get('text', '') for entry in transcript]).strip()
            if final_text:
                save_transcript_output(
                    os.path.join(folder, f"{slug}_transcricao_yt_api{ext}"),
                    final_text, ext, url, video_title,
                    metadata=metadata,
                    transcript_language=lang_label or "youtube-transcript-api",
                )
                return
        print("[AVISO] Nenhuma transcricao encontrada.")
    except Exception as e:
        print(f"[ERRO] {str(e)}")

def get_transcript_pytubefix(url, folder, slug, ext, video_title, metadata):
    print("\n[2/3] pytubefix...")
    try:
        yt = YouTube(url)
        caption = None
        code_used = ""
        for code in ['pt', 'pt-BR', 'a.pt', 'a.pt-BR', 'en', 'a.en']:
            if code in yt.captions:
                caption = yt.captions[code]
                code_used = code
                break

        if not caption and yt.captions:
            caption = list(yt.captions.values())[0]
            code_used = getattr(caption, "code", "") or "primeira disponível"

        if caption:
            final_text = limpar_legenda(caption.generate_srt_captions())
            if final_text:
                lang_label = f"pytubefix — legenda `{code_used}`" if code_used else "pytubefix"
                save_transcript_output(
                    os.path.join(folder, f"{slug}_transcricao_pytubefix{ext}"),
                    final_text, ext, url, video_title,
                    metadata=metadata,
                    transcript_language=lang_label,
                )
            else:
                print("[ERRO] Transcricao vazia.")
        else:
            print("[ERRO] Nenhuma legenda encontrada.")
    except Exception as e:
        print(f"[ERRO] {str(e)}")

def get_transcript_ytdlp(url, folder, slug, video_id, ext, video_title, metadata):
    print("\n[3/3] yt-dlp...")
    sub_lang_requested = "pt"
    try:
        sub_file_base = os.path.join(folder, f"_sub_temp_{video_id}")

        subprocess.run([
            "yt-dlp", "--write-auto-sub", "--sub-lang", sub_lang_requested, "--sub-format", "srt",
            "--skip-download", "--no-warnings", "-o", sub_file_base + ".%(ext)s", url
        ], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)

        found_path = next((os.path.join(folder, f) for f in os.listdir(folder) if f.startswith(f"_sub_temp_{video_id}") and f.endswith(('.srt', '.vtt'))), None)
        lang_from_file = ""
        if found_path:
            base = os.path.basename(found_path)
            for part in base.replace(".", " ").split():
                if len(part) == 2 or (len(part) == 5 and part[2] == "-"):
                    lang_from_file = part
                    break

        if found_path:
            with open(found_path, "r", encoding="utf-8", errors="replace") as arq:
                final_text = limpar_legenda(arq.read())

            if final_text:
                lang_label = (
                    f"yt-dlp — idioma solicitado `{sub_lang_requested}`"
                    + (f", arquivo `{lang_from_file}`" if lang_from_file else "")
                )
                save_transcript_output(
                    os.path.join(folder, f"{slug}_transcricao_ytdlp{ext}"),
                    final_text, ext, url, video_title,
                    metadata=metadata,
                    transcript_language=lang_label,
                )
            else: print("[ERRO] Legenda vazia.")
            
            os.remove(found_path)
        else:
            print("[ERRO] Nenhum arquivo baixado.")
    except Exception as e:
        print(f"[ERRO] {str(e)}")

def run_transcriptions(url, metodos=None, folder=None, slug=None, ext=".txt"):
    """
    Gera transcrições em out/ (ou em folder) usando um ou mais métodos.
    metodos: None = todos; ou conjunto/lista com 'yt-api', 'pytubefix', 'ytdlp'.
    folder/slug: se omitidos, são obtidos automaticamente (título via yt-dlp).
    folder: caminho absoluto; a pasta é criada se não existir.
    ext: extensão dos arquivos (.txt ou .md); use normalize_output_ext.
    Retorna False se a URL for inválida.
    """
    video_id = get_video_id(url) if url else None
    if not video_id:
        print("[ERRO] Link inválido ou vazio!")
        return False

    if folder is None:
        folder = out_dir()
    else:
        folder = os.path.abspath(os.path.expanduser(folder))
        os.makedirs(folder, exist_ok=True)
    metadata = {}
    try:
        metadata = fetch_video_metadata(url)
    except Exception as e:
        print(f"[AVISO] Não foi possível obter metadados do vídeo: {e}")

    video_title = (metadata.get("title") or "").strip()
    if slug is None:
        slug = slugify_title(video_title) or video_id
        print(f"[INFO] Arquivos usarão o prefixo: {slug}")
    if not video_title:
        video_title = slug

    ext = normalize_output_ext(ext)

    ativos = {"yt-api", "pytubefix", "ytdlp"} if metodos is None else set(metodos)
    if "yt-api" in ativos:
        get_transcript_ytapi(video_id, folder, slug, ext, url, video_title, metadata)
    if "pytubefix" in ativos:
        get_transcript_pytubefix(url, folder, slug, ext, video_title, metadata)
    if "ytdlp" in ativos:
        get_transcript_ytdlp(url, folder, slug, video_id, ext, video_title, metadata)
    return True

def download_media(url, folder, mode, slug):
    print(f"\n[INICIO] Download de {mode}...")
    try:
        opts = {
            'outtmpl': os.path.join(folder, f"{slug}.%(ext)s"),
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

    folder = out_dir()
    try:
        title = fetch_video_title(url)
    except Exception as e:
        print(f"[AVISO] Não foi possível obter o título do vídeo: {e}")
        title = ""
    slug = slugify_title(title) or video_id
    print(f"[INFO] Arquivos usarão o prefixo: {slug}")

    while True:
        print("\nO que você deseja fazer?\n1. Gerar Transcrições (3 métodos)\n2. Baixar VIDEO (MP4)\n3. Baixar AUDIO (MP3)\n0. Sair")
        choice = input("\nEscolha: ").strip()
        
        if choice == '1':
            run_transcriptions(url, folder=folder, slug=slug)
        elif choice == '2': download_media(url, folder, 'video', slug)
        elif choice == '3': download_media(url, folder, 'audio', slug)
        elif choice == '0': break
        else: print("[AVISO] Inválido.")

if __name__ == "__main__":
    main()
