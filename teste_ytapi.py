import os
import re
from youtube_transcript_api import YouTubeTranscriptApi

from out_dir import out_dir

url = input("Digite a URL do YouTube: ").strip()
match = re.search(r'(?:v=|\/|embed\/|shorts\/|be\/)([0-9A-Za-z_-]{11})', url)
video_id = match.group(1) if match else url

print(f"\n[INFO] ID do video detectado: {video_id}")
print("[INFO] Conectando com o YouTube...\n")

try:
    todas_legendas = YouTubeTranscriptApi.list_transcripts(video_id)
    
    print("=== LEGENDAS DETECTADAS ===")
    for l in todas_legendas:
        tipo = "Automatica" if l.is_generated else "Manual"
        print(f" > Idioma: {l.language} | Codigo: '{l.language_code}' | Tipo: {tipo}")
    print("===========================\n")
    
    transcript = None
    
    print("[INFO] Tentando baixar as legendas na ordem PT -> PT-BR -> EN:")
    for lang in [['pt'], ['pt-BR'], ['pt', 'pt-BR'], ['en']]:
        try:
            print(f"  -> Buscando por '{lang}'...")
            t_obj = todas_legendas.find_transcript(lang)
            transcript = t_obj.fetch()
            print(f"  [OK] Encontrada ({t_obj.language})!")
            break
        except Exception as e:
            print(f"  [FALHA] Não disponível: {str(e).splitlines()[0]}")
            continue
            
    if not transcript:
        try:
            print("\n[INFO] Nenhuma legenda nos idiomas preferidos. Pegando a primeira disponivel...")
            for t in todas_legendas:
                print(f"  -> Baixando idioma: {t.language}...")
                transcript = t.fetch()
                print("  [OK] Legenda baixada!")
                break
        except Exception as e:
            print(f"  [ERRO] Falhou ao baixar qualquer legenda: {e}")

    if transcript:
        texto = " ".join([t.get('text', '') for t in transcript]).strip()
        dest = os.path.join(out_dir(), "resultado_ytapi.txt")
        with open(dest, "w", encoding="utf-8") as f:
            f.write(texto)
        print(f"\n[OK] Transcricao salva em: {dest}")
    else:
        print("\n[AVISO] Nenhuma transcricao extraida no final do processo.")
        
except Exception as e:
    print(f"\n[ERRO GERAL] A API nao conseguiu ler os dados do video:\n{e}")
