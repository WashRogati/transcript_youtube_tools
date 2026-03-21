# Como usar este projeto

Ferramentas em Python para **baixar áudio (MP3)**, **vídeo (MP4)** e **gerar texto a partir de legendas/transcrições** de vídeos do YouTube.

---

## 1. Preparar o ambiente (uma vez)

Na pasta do projeto, execute o script **`init.sh`** (cria o venv, instala dependências e a pasta `out/`):

```bash
chmod +x init.sh
./init.sh
```

Ou, manualmente, os mesmos passos:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U -r requirements.txt
mkdir -p out
```

A pasta **`out/`** guarda transcrições e mídia baixada; os scripts também a criam automaticamente se não existir.

No macOS, para converter áudio em MP3 e mesclar faixas de vídeo, é necessário **FFmpeg** (por exemplo: `brew install ffmpeg`).

> Se o Python do sistema (Homebrew) bloquear `pip install` global, use sempre o **venv** como acima.

---

## 2. Forma principal: menu interativo (`tools.py`)

Com o venv ativado, na pasta do projeto:

```bash
source .venv/bin/activate
python tools.py
```

1. Cole o **link do vídeo** (URL normal, `youtu.be`, Shorts, etc.).
2. Escolha no menu:
   - **1** — Gera transcrições com **três métodos** em sequência (arquivos `.txt` na pasta do projeto).
   - **2** — Baixa **vídeo** em MP4 (melhor qualidade disponível compatível com as opções do script).
   - **3** — Baixa **áudio** em **MP3** (192 kbps).
   - **0** — Sair.

### Onde os arquivos são salvos

Tudo é gravado na pasta **`out/`** na raiz do projeto (criada automaticamente se não existir).

| Ação | Arquivos gerados (exemplos, todos em `out/`) |
|------|-----------------------------|
| Opção 1 — transcrições | `out/<slug>_transcricao_yt_api.txt`, `out/<slug>_transcricao_pytubefix.txt`, `out/<slug>_transcricao_ytdlp.txt` |
| Opção 2 — vídeo | `out/<slug>.mp4` (ou extensão que o yt-dlp escolher) |
| Opção 3 — áudio | `out/<slug>.mp3` |

O **`<slug>`** é o título do vídeo normalizado (minúsculas, sem acentos, hífens no lugar de espaços). Se o título não puder ser obtido, usa-se o ID do vídeo. Ao iniciar, o programa mostra `[INFO] Arquivos usarão o prefixo: ...`.

O método **yt-dlp** na transcrição usa o comando `yt-dlp` no terminal; com o venv ativado, ele costuma estar em `.venv/bin/yt-dlp`. Se der erro de “comando não encontrado”, rode o `tools.py` com o venv ativado ou use o caminho completo: `.venv/bin/python tools.py`.

---

## 2.1. Só transcrições (`transcrever.py`)

Para gerar transcrições **sem o menu interativo** (mesmos arquivos em `out/` que a opção **1** do `tools.py`):

```bash
source .venv/bin/activate
python transcrever.py "https://www.youtube.com/watch?v=..."
```

Se você não passar a URL, o script pede no terminal.

Escolher **um ou mais** métodos (padrão: os três):

```bash
python transcrever.py "URL" --metodo yt-api
python transcrever.py "URL" --metodo pytubefix --metodo ytdlp
```

Valores de `--metodo`: `yt-api`, `pytubefix`, `ytdlp`.

Outra pasta de saída (em vez do `out/` padrão do projeto):

```bash
python transcrever.py "URL" -o /caminho/para/minha_pasta
python transcrever.py "URL" --out ~/Downloads/transcricoes
```

A pasta é criada automaticamente se não existir.

Salvar como **Markdown** (`.md`) em vez de `.txt`:

```bash
python transcrever.py "URL" --markdown
python transcrever.py "URL" -m
```

Com **`-m` / `--markdown`**, o arquivo `.md` segue este formato:

1. Primeira linha: **título do vídeo** (obtido via yt-dlp).
2. Linha **`**Link:**`** seguida da URL usada no comando.
3. Título de nível 3 **`### Conteúdo`** e, abaixo, o texto da transcrição.
4. Ao final: data e hora locais em que a transcrição foi gerada (`*Transcrito em: ...*`).

Útil para vaults Obsidian e notas em Markdown.

---

## 3. Scripts avulsos (só áudio ou só vídeo)

São atalhos que pedem a URL no terminal e gravam os arquivos em **`out/`** (na raiz do projeto).

| Script | Função |
|--------|--------|
| `baixar_audio_ytdlp.py` | Áudio em **MP3** (yt-dlp + FFmpeg) |
| `baixar_video_ytdlp.py` | Vídeo em **MP4** (quando disponível no formato escolhido) |

Exemplo (com venv):

```bash
cd /caminho/para/transcript_youtube_tools
source .venv/bin/activate
python baixar_audio_ytdlp.py
```

Existem também variantes com **pytubefix** (`baixar_audio_pytubefix.py`, `baixar_video_pytubefix.py`) para testes ou uso alternativo.

---

## 4. “Adicionar” o script para usar com mais facilidade

Não é obrigatório instalar nada no sistema além do venv. Três jeitos comuns:

### A) Atalho no terminal (alias)

No seu `~/.zshrc` (ou `~/.bashrc`), você pode definir um atalho para a pasta do projeto e outro para rodar o menu:

```bash
export YT_TOOLS="$HOME/Projects/wrogati/transcript_youtube_tools"
alias yt-tools='cd "$YT_TOOLS" && source .venv/bin/activate && python tools.py'
```

Abra um novo terminal e digite `yt-tools` para abrir o menu.

### B) Caminho absoluto sem alias

Sempre que quiser:

```bash
source /caminho/completo/para/transcript_youtube_tools/.venv/bin/activate
python /caminho/completo/para/transcript_youtube_tools/tools.py
```

### C) Atalho no Cursor / VS Code

1. **Terminal integrado**: `Terminal` → `New Terminal`, `cd` até a pasta do projeto, `source .venv/bin/activate`, `python tools.py`.
2. **Tarefa (Tasks)** ou **Run**: configure um comando que execute `.venv/bin/python tools.py` com `cwd` na pasta do projeto (opcional; depende de como você prefere trabalhar no editor).

---

## 5. Problemas frequentes

- **Erro no yt-dlp**: atualize o pacote (`pip install -U yt-dlp` dentro do venv).
- **MP3 falha**: confira se o **FFmpeg** está instalado e no `PATH`.
- **Sem legenda / transcrição vazia**: nem todo vídeo tem legendas ou transcrição automática no idioma esperado; os três métodos do menu podem se comportar de forma diferente por vídeo.
