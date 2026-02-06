import os
import streamlit as st
from dotenv import load_dotenv
import tempfile
from urllib.parse import urlparse

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from import_file import *

load_dotenv()

PROVEDORES = {
    "Groq": {
        "modelos": [
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
        ],
        "chat_class": ChatGroq,
        "env_key": "GROQ_API_KEY",
    },
    "OpenAI": {
        "modelos": [
            "gpt-5",
            "gpt-5-mini",
            "gpt-5-nano",
            "gpt-4.1",
            "gpt-4.1-mini",
            "gpt-4o",
            "gpt-4o-mini",
            "o3",
            "o3-mini",
        ],
        "chat_class": ChatOpenAI,
        "env_key": "OPENAI_API_KEY",
    },
}

TIPOS_ARQUIVOS = ["Site", "Youtube", "CSV", "PDF", "TXT"]
MEMORIA = InMemoryChatMessageHistory()


def normalize_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return ""
    return url


def init_state():
    if "memoria" not in st.session_state:
        st.session_state["memoria"] = InMemoryChatMessageHistory()
    if "chat" not in st.session_state:
        st.session_state["chat"] = None

    if "provedor" not in st.session_state:
        st.session_state["provedor"] = os.getenv("DEFAULT_PROVIDER", "OpenAI")

    if "modelo" not in st.session_state:
        default_openai = os.getenv("DEFAULT_MODEL_OPENAI", "gpt-4o-mini")
        default_groq = os.getenv("DEFAULT_MODEL_GROQ", "llama-3.1-8b-instant")
        st.session_state["modelo"] = default_openai if st.session_state["provedor"] == "OpenAI" else default_groq

    if "tipo_arquivo" not in st.session_state:
        st.session_state["tipo_arquivo"] = os.getenv("DEFAULT_FILE_TYPE", "Site")

    if "arquivo" not in st.session_state:
        st.session_state["arquivo"] = os.getenv("DEFAULT_SOURCE", "")

    ensure_initialized()


def get_api_key(provedor: str, sidebar_value: str | None = None) -> str:
    env_key = PROVEDORES[provedor]["env_key"]
    from_env = os.getenv(env_key, "") or ""
    from_sidebar = (sidebar_value or "").strip()
    return from_sidebar if from_sidebar else from_env.strip()


def load_files(tipo_arquivos, arquivo):
    if tipo_arquivos == "Site":
        return load_site(arquivo)
    if tipo_arquivos == "Youtube":
        return load_youtube(arquivo)

    if tipo_arquivos == "PDF":
        arquivo.seek(0)  # <- ESSENCIAL
        pdf_bytes = arquivo.read()
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp:
            temp.write(pdf_bytes)
            nome_temp = temp.name
        return load_pdf(nome_temp)

    if tipo_arquivos == "CSV":
        arquivo.seek(0)
        csv_bytes = arquivo.read()
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp:
            temp.write(csv_bytes)
            nome_temp = temp.name
        return load_csv(nome_temp)

    if tipo_arquivos == "TXT":
        arquivo.seek(0)
        txt_bytes = arquivo.read()
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp:
            temp.write(txt_bytes)
            nome_temp = temp.name
        return load_text(nome_temp)

    return ""


def load_model(provedor: str, modelo: str, api_key: str, tipo_arquivo: str | None, arquivo):
    if not api_key:
        st.error(
            f"API key não encontrada. Configure no .env ({PROVEDORES[provedor]['env_key']}) ou informe na sidebar."
        )
        return

    documento = ""
    if tipo_arquivo and arquivo:
        try:
            documento = load_files(tipo_arquivo, arquivo)
        except Exception:
            documento = ""

    system_message = """Você é um assistente amigável chamado Oráculo.

Você possui acesso às seguintes informações vindas de um documento (se fornecido) {}:

####
{}
####

Utilize as informações fornecidas para basear as suas respostas.

Sempre que houver $ na sua saída, substitua por S.

Se a informação do documento for algo como Just a moment...Enable Javascript and cookies to continue
sugira ao usuário carregar novamente o Oráculo!
""".format(tipo_arquivo or "Nenhum", documento or "")

    template = ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            MessagesPlaceholder("chat_history"),
            ("user", "{input}"),
        ]
    )

    chat_class = PROVEDORES[provedor]["chat_class"]
    chat = chat_class(model=modelo, api_key=api_key)
    chain = template | chat

    st.session_state["chat"] = chain


def ensure_initialized():
    provedor = st.session_state.get("provedor", "OpenAI")
    modelo = st.session_state.get("modelo", "gpt-4o-mini")

    tipo_arquivo = st.session_state.get("tipo_arquivo")
    arquivo = st.session_state.get("arquivo")

    api_key = get_api_key(provedor, st.session_state.get(f"api_key_{provedor}", ""))

    # normaliza URL só se houver texto
    if tipo_arquivo in ["Site", "Youtube"] and isinstance(arquivo, str):
        arquivo = normalize_url(arquivo)
        st.session_state["arquivo"] = arquivo

    load_model(provedor, modelo, api_key, tipo_arquivo, arquivo)


def chat_page():
    chat = st.session_state.get("chat")
    memoria = st.session_state.get("memoria", MEMORIA)

    for msg in memoria.messages:
        role = "user" if msg.type == "human" else "assistant"
        st.chat_message(role).markdown(msg.content)

    if st.button("🗑️ Limpar conversa"):
        st.session_state["memoria"] = InMemoryChatMessageHistory()
        st.rerun()

    input_usuario = st.chat_input("Envie sua dúvida")
    if input_usuario:
        if chat is None:
            st.error("Não foi possível iniciar o Oráculo (verifique a API key).")
            st.stop()

        st.chat_message("user").markdown(input_usuario)
        memoria.add_user_message(input_usuario)

        with st.chat_message("assistant"):
            resposta = st.write_stream(
                (
                    getattr(chunk, "content", "") or ""
                    for chunk in chat.stream(
                        {"input": input_usuario, "chat_history": memoria.messages}
                    )
                )
            )

        memoria.add_ai_message(resposta or "")
        st.session_state["memoria"] = memoria


def side_bar():
    with st.sidebar:
        tabs = st.tabs(["Upload de arquivos", "Seleção de modelos"])

        with tabs[0]:
            tipo_arquivo = st.selectbox(
                "Selecione o tipo de arquivo",
                TIPOS_ARQUIVOS,
                index=TIPOS_ARQUIVOS.index(st.session_state.get("tipo_arquivo", "Site"))
                if st.session_state.get("tipo_arquivo", "Site") in TIPOS_ARQUIVOS
                else 0,
            )
            st.session_state["tipo_arquivo"] = tipo_arquivo

            if tipo_arquivo in ["Site", "Youtube"]:
                arquivo = st.text_input(
                    f"Digite a URL do {tipo_arquivo} (opcional)",
                    value=st.session_state.get("arquivo", ""),
                )
                st.session_state["arquivo"] = arquivo
            else:
                ext = tipo_arquivo.lower()
                arquivo_up = st.file_uploader(
                    f"Faça o upload do arquivo {tipo_arquivo} (opcional)",
                    type=[ext],
                )
                if arquivo_up is not None:
                    st.session_state["arquivo"] = arquivo_up
                elif not isinstance(st.session_state.get("arquivo"), str):
                    # se não enviou nada, limpa para evitar reuso involuntário
                    st.session_state["arquivo"] = ""

        with tabs[1]:
            provedor = st.selectbox(
                "Selecione o provedor",
                list(PROVEDORES.keys()),
                index=list(PROVEDORES.keys()).index(st.session_state["provedor"])
                if st.session_state["provedor"] in PROVEDORES
                else 0,
            )

            modelos = PROVEDORES[provedor]["modelos"]
            default_model = st.session_state["modelo"] if st.session_state["modelo"] in modelos else modelos[0]
            modelo = st.selectbox("Selecione o modelo", modelos, index=modelos.index(default_model))

        st.session_state["provedor"] = provedor
        st.session_state["modelo"] = modelo

        # recarrega automaticamente (sem botão de inicializar)
        if st.session_state.get("_last_cfg") != (
            st.session_state["provedor"],
            st.session_state["modelo"],
            st.session_state.get("tipo_arquivo"),
            str(type(st.session_state.get("arquivo"))),
            st.session_state.get("arquivo") if isinstance(st.session_state.get("arquivo"), str) else None,
            st.session_state.get(f"api_key_{st.session_state['provedor']}", ""),
        ):
            st.session_state["_last_cfg"] = (
                st.session_state["provedor"],
                st.session_state["modelo"],
                st.session_state.get("tipo_arquivo"),
                str(type(st.session_state.get("arquivo"))),
                st.session_state.get("arquivo") if isinstance(st.session_state.get("arquivo"), str) else None,
                st.session_state.get(f"api_key_{st.session_state['provedor']}", ""),
            )
            st.session_state["chat"] = None
            ensure_initialized()


def main():
    init_state()
    side_bar()
    chat_page()


if __name__ == "__main__":
    app_title = os.getenv("APP_TITLE", "Oráculo")
    st.header(f"🤖 Bem vindo ao {app_title}", divider=True)
    main()
