from pytubefix import YouTube

from out_dir import out_dir

url = input("Digite a URL do YouTube: ").strip()

try:
    print("Buscando video com pytubefix...")
    yt = YouTube(url)
    
    stream = yt.streams.get_highest_resolution()
    print(f"Baixando: {yt.title}")
    
    stream.download(output_path=out_dir())
    print("Download de video finalizado!")
except Exception as e:
    print(f"ERRO: {e}")
