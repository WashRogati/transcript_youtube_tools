import os
import re
from pytubefix import YouTube

from out_dir import out_dir

url = input("Digite a URL do YouTube: ").strip()

try:
    yt = YouTube(url)
    
    caption = yt.captions.get('pt') or yt.captions.get('a.pt') or yt.captions.get('en')
    
    if caption:
        srt = caption.generate_srt_captions()
        
        linhas = []
        for linha in srt.splitlines():
            linha = re.sub(r'<[^>]+>', '', linha.strip())
            if linha and not linha.isdigit() and '-->' not in linha:
                if not linhas or linhas[-1] != linha: linhas.append(linha)
                
        dest = os.path.join(out_dir(), "resultado_pytubefix.txt")
        with open(dest, "w", encoding="utf-8") as f:
            f.write(" ".join(linhas))
            
        print(f"Transcricao gerada: {dest}")
    else:
        print("Nenhuma legenda encontrada.")
except Exception as e:
    print(f"ERRO: {e}")
