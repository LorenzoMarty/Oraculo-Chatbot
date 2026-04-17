# Oráculo — Chat com IA

O **Oráculo** é uma aplicação em **Streamlit** que permite conversar com LLMs utilizando **conteúdo de arquivos, sites ou vídeos do YouTube** como contexto.

O projeto combina:

* **Streamlit** para interface interativa
* **LangChain** para orquestração do LLM
* **RAG simples baseado em documentos carregados**
* **Suporte a múltiplas fontes de dados**

## Funcionalidades

- Chat interativo com IA
- Leitura de **PDF, CSV e TXT**
- Análise de **sites**
- Extração de conteúdo de **vídeos do YouTube**
- Respostas baseadas **somente no documento carregado**
- Troca dinâmica de **modelo e provedor**
- Botão para **limpar conversa**
- Streaming de resposta em tempo real

## Arquitetura

Fluxo principal:

1. O usuário envia um arquivo/link
2. O usuário escolhe o modelo de IA e insere sua key
3. O usuário faz perguntas no chat
4. O chat responde baseado no arquivo/link fornecido

## Instalação

```bash
git clone https://github.com/LorenzoMarty/Oraculo-Chatbot.git
cd Oraculo-Chatbot

python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

## Variáveis de ambiente

Crie um arquivo `.env`:

```
OPENAI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here

DEFAULT_PROVIDER=OpenAI
DEFAULT_MODEL_OPENAI=gpt-4o-mini
DEFAULT_MODEL_GROQ=llama-3.1-8b-instant

APP_TITLE=Oráculo
```

## Executando o projeto

```bash
streamlit run app_streamlit.py
```

## Tecnologias

- Python
- Streamlit
- LangChain
- OpenAI API
- Groq API

## Autor

**Lorenzo Marty**\
GitHub: https://github.com/LorenzoMarty
