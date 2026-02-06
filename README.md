# 🤖 Oráculo — Chat com IA baseado em documentos

O **Oráculo** é uma aplicação em **Streamlit** que permite conversar com modelos de linguagem (OpenAI ou Groq) utilizando **conteúdo de arquivos, sites ou vídeos do YouTube** como contexto.

O projeto combina:

* **Streamlit** para interface interativa
* **LangChain** para orquestração do LLM
* **RAG simples baseado em documentos carregados**
* **Suporte a múltiplas fontes de dados**

---

# ✨ Funcionalidades

* 💬 Chat interativo com IA
* 📄 Leitura de **PDF, CSV e TXT**
* 🌐 Análise de **sites**
* ▶️ Extração de conteúdo de **vídeos do YouTube**
* 🧠 Respostas baseadas **somente no documento carregado**
* 🔁 Troca dinâmica de **modelo e provedor**
* 🗑️ Botão para **limpar conversa**
* ⚡ Streaming de resposta em tempo real

---

# 🏗️ Arquitetura

```
Streamlit UI
   │
   ├── Upload / URL / YouTube
   │
   ├── Loaders (LangChain Community)
   │       ├── PyPDFLoader
   │       ├── CSVLoader
   │       ├── TextLoader
   │       ├── WebBaseLoader
   │       └── YoutubeLoader
   │
   └── LLM Chain
           ├── Prompt com contexto do documento
           ├── Memória de chat
           └── Modelo (OpenAI ou Groq)
```

---

# 📦 Requisitos

Crie um ambiente virtual e instale:

```
streamlit
langchain
langchain-community
langchain-groq
langchain-openai
python-dotenv
bs4
pypdf
unstructured
fake_useragent
youtube_transcript_api
requests
lxml
tiktoken
```

---

# 🔑 Variáveis de ambiente

Crie um arquivo **`.env`** na raiz:

```
OPENAI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here

DEFAULT_PROVIDER=OpenAI
DEFAULT_MODEL_OPENAI=gpt-4o-mini
DEFAULT_MODEL_GROQ=llama-3.1-8b-instant

APP_TITLE=Oráculo
```

Opcional (remove warning de web scraping):

```
USER_AGENT=OraculoBot/1.0
```

---

# ▶️ Como executar

```
streamlit run app.py
```

Depois abra no navegador:

```
http://localhost:8501
```

---

# 🧪 Fluxo de uso

1. Escolha o **tipo de fonte**:

   * Site
   * YouTube
   * PDF
   * CSV
   * TXT

2. Forneça o arquivo ou URL (opcional).

3. Selecione:

   * **Provedor** (OpenAI ou Groq)
   * **Modelo**

4. Converse com o Oráculo.

As respostas serão **baseadas no conteúdo carregado**.

---

# ⚠️ Limitações atuais

* Não utiliza embeddings vetoriais (RAG completo).
* Documento é carregado **inteiro no prompt**.
* Memória é **apenas da sessão atual**.
* Não há persistência em banco de dados.

---

# 📚 Tecnologias

* Python
* Streamlit
* LangChain
* OpenAI API
* Groq API

---

# 👨‍💻 Autor

Projeto desenvolvido para estudo e construção de aplicações reais com **IA generativa, RAG e interfaces web em Python**.

---

Se este projeto te ajudou, considere evoluí-lo para produção 🚀
