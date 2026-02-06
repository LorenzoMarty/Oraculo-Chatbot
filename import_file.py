import os
import streamlit as st
from langchain_community.document_loaders import (
    WebBaseLoader,
    YoutubeLoader,
    CSVLoader,
    PyPDFLoader,
    TextLoader,
)
from dotenv import load_dotenv
from fake_useragent import UserAgent

load_dotenv()

def load_site(url):
    site_conteudo = ''
    for i in range(5):
        try:
            os.environ['USER_AGENT'] = UserAgent().random
            loader = WebBaseLoader(url)
            site_completo = loader.load()
            site_conteudo = '\n\n'.join(doc.page_content for doc in site_completo)
            if site_conteudo.strip():
                break
        except:
            print(f'Erro ao consultar o site {i+1}')
    if site_conteudo == '':
        st.error('Não foi possível carregar o site')
        st.stop()
    return site_conteudo

def load_youtube(video_id):
    loader = YoutubeLoader(video_id, add_video_info=False, language='pt')
    video_completo = loader.load()
    video_conteudo = '\n\n'.join(video.page_content for video in video_completo)
    return video_conteudo

def load_csv(caminho):
    loader = CSVLoader(caminho)
    csv_completo = loader.load()
    csv_conteudo = '\n\n'.join(row.page_content for row in csv_completo)
    return csv_conteudo

def load_pdf(caminho):
    loader = PyPDFLoader(caminho)
    pdf_completo = loader.load()
    pdf_conteudo = '\n\n'.join(pf.page_content for pf in pdf_completo)  # ✅ pf, não pdf
    return pdf_conteudo

def load_text(caminho):
    loader = TextLoader(caminho)
    text_completo = loader.load()
    text_conteudo = '\n\n'.join(t.page_content for t in text_completo)
    return text_conteudo
