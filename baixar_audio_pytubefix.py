import os
from pytubefix import YouTube

url = input("Digite a URL do YouTube: ").strip()

try:
    print("Buscando audio com pytubefix...")
    yt = YouTube(url)
    
    stream = yt.streams.get_audio_only()
    print(f"Baixando: {yt.title}")
    
    out_file = stream.download()
    
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    
    # Sobrescreve se o mp3 ja existir
    if os.path.exists(new_file):
        os.remove(new_file)
        
    os.rename(out_file, new_file)
    
    print("Download de audio finalizado!")
except Exception as e:
    print(f"ERRO: {e}")
