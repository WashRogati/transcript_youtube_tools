from pytubefix import YouTube

url = input("Digite a URL do YouTube: ").strip()

try:
    print("Buscando video com pytubefix...")
    yt = YouTube(url)
    
    stream = yt.streams.get_highest_resolution()
    print(f"Baixando: {yt.title}")
    
    stream.download()
    print("Download de video finalizado!")
except Exception as e:
    print(f"ERRO: {e}")
