#!/usr/bin/env python3
"""
Gera transcrições (legendas/texto) em out/ sem usar o menu do tools.py.
"""
import argparse
import sys

from tools import run_transcriptions

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Gera transcrições do YouTube em out/ (youtube-transcript-api, pytubefix, yt-dlp)."
    )
    parser.add_argument(
        "url",
        nargs="?",
        help="URL do vídeo (se omitido, será pedida no terminal)",
    )
    parser.add_argument(
        "--metodo",
        action="append",
        choices=["yt-api", "pytubefix", "ytdlp"],
        metavar="M",
        help="Rodar só este método (pode repetir). Padrão: os três.",
    )
    args = parser.parse_args()

    url = (args.url or "").strip() or input("URL do vídeo: ").strip()
    metodos = args.metodo if args.metodo else None

    if not run_transcriptions(url, metodos=metodos):
        sys.exit(1)


if __name__ == "__main__":
    main()
