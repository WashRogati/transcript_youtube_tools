#!/usr/bin/env python3
"""
Gera transcrições (legendas/texto) em out/ (ou pasta --out) sem usar o menu do tools.py.
"""
import argparse
import sys

from tools import normalize_output_ext, run_transcriptions

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Gera transcrições do YouTube (youtube-transcript-api, pytubefix, yt-dlp)."
    )
    parser.add_argument(
        "url",
        nargs="?",
        help="URL do vídeo (se omitido, será pedida no terminal)",
    )
    parser.add_argument(
        "-o",
        "--out",
        metavar="PASTA",
        help="Pasta de saída (padrão: out/ na raiz do projeto)",
    )
    parser.add_argument(
        "-m",
        "--markdown",
        action="store_true",
        help="Salvar como .md em vez de .txt",
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

    pasta = (args.out or "").strip() or None
    ext = normalize_output_ext("md" if args.markdown else "txt")
    if not run_transcriptions(url, metodos=metodos, folder=pasta, ext=ext):
        sys.exit(1)


if __name__ == "__main__":
    main()
