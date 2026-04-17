import requests
from bs4 import BeautifulSoup
import pandas as pd
from pypdf import PdfReader
import yt_dlp


# 🌐 SITE
def load_site(url: str) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # remove scripts e styles
        for tag in soup(["script", "style"]):
            tag.decompose()

        text = soup.get_text(separator="\n")

        return text.strip()

    except Exception as e:
        raise Exception(f"Erro ao carregar site: {e}")


# 🎥 YOUTUBE (transcrição)
def load_youtube(url: str) -> str:
    try:
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["pt", "en"],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            subtitles = info.get("subtitles") or info.get("automatic_captions")

            if not subtitles:
                return "Sem transcrição disponível"

            # pega primeira legenda disponível
            lang = list(subtitles.keys())[0]
            subtitle_url = subtitles[lang][0]["url"]

            sub_response = requests.get(subtitle_url)
            return sub_response.text

    except Exception as e:
        raise Exception(f"Erro ao carregar YouTube: {e}")


# 📊 CSV
def load_csv(caminho: str) -> str:
    try:
        df = pd.read_csv(caminho)
        return df.to_string()

    except Exception as e:
        raise Exception(f"Erro ao carregar CSV: {e}")


# 📄 PDF
def load_pdf(caminho: str) -> str:
    try:
        reader = PdfReader(caminho)
        text = []

        for page in reader.pages:
            text.append(page.extract_text() or "")

        return "\n\n".join(text)

    except Exception as e:
        raise Exception(f"Erro ao carregar PDF: {e}")


# 📝 TXT
def load_text(caminho: str) -> str:
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return f.read()

    except Exception as e:
        raise Exception(f"Erro ao carregar TXT: {e}")


# 🔁 ROUTER
def load_file(tipo: str, caminho: str) -> str:
    tipo = tipo.lower()

    if tipo == "site":
        return load_site(caminho)

    elif tipo in ["youtube", "video"]:
        return load_youtube(caminho)

    elif tipo == "csv":
        return load_csv(caminho)

    elif tipo == "pdf":
        return load_pdf(caminho)

    elif tipo in ["txt", "text"]:
        return load_text(caminho)

    else:
        raise ValueError(f"Tipo de arquivo não suportado: {tipo}")
