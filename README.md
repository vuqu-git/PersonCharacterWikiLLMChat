# 🧑‍💻 Person and Character Wiki Bot

A modular, full-stack RAG (Retrieval-Augmented Generation) assistant for exploring and chatting about Wikipedia or Fandom pages of fictional characters and real people.  
Supports both file upload (offline) and online scraping, and adapts for any structured Wiki/biographical HTML.

---

## ✨ Features

- **🤖 Smart LLM Chat & Facts:**
    - Ask any question about the loaded person or character—bot answers contextually using automatically extracted facts!
    - Combines open-source local sentence embeddings with Perplexity API for robust retrieval and reasoning.

- **🔄 Two Processing Modes:**
    - 📁 Upload a saved HTML page from any Wikipedia, Fandom, or biographical site (*right-click → Save As...*)
    - 🌍 Enter a live Wiki URL (scrape online, if allowed—may be blocked)

- **🖥️ Gradio Web Interface:**
    - Clean, tabbed UI for profile input and conversational Q&A

---

## 🚀 Quickstart

1. **Clone and install**
    ```
    git clone https://github.com/YOUR_USERNAME/person-character-wiki-bot
    cd person-character-wiki-bot
    pip install -r requirements.txt
    ```
2. **Set up your `.env`**
    ```
    PPLX_API_KEY=sk-xxxxxxx...
    ```
3. **Launch!**
    ```
    python app_wiki.py
    # → Open http://localhost:5001 in your browser
    ```

---

## 🛠️ How It Works

- **Step 1: Choose a Mode**
    - 📁 *Upload HTML*: Great for JS-heavy or anti-bot protected pages—works offline!
    - 🌐 *Wiki URL/Mock*: Live scraping (if allowed) or repeatable mock test

- **Step 2:** The system parses/splits HTML, builds vector index with local embeddings

- **Step 3:** LLM summarizes interesting facts

- **Step 4:** 🗣️ Chat with the bot for context-aware Q&A

#### Tech Stack

- **Python**
- **Gradio** (`Blocks`, `Chatbot`)
- **LlamaIndex** (`VectorStoreIndex`, node splitting, prompts)
- **Perplexity API** (LLM with temperature/token controls)
- **HuggingFace Embeddings**
- **BeautifulSoup**
- **Modular design** for easy extension

---

## 💡 Usage Notes

- ✨ **Upload HTML File** for the most reliable results (offline-ready, bypasses anti-bot)
- 🔎 Web scraping may hit 403/empty results on some sites with strict protection
- 🌍 LLM API usage is subject to rate limits if using hosted models

---
## 🚀 Quick Start

### Prerequisites

- Python 3.11+, < 3.13
- A Perplexity API key (recommended for full features — mock/HTML upload available without)

### Installation

1. Clone the repository:
    ```
    git clone https://github.com/vuqu-git/person-character-wiki-bot.git
    cd person-character-wiki-bot
    ```

2. Create a virtual environment:
    ```
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install dependencies:
    ```
    pip install -r requirements.txt
    ```

4. Add your Perplexity API key to `.env`:
    ```
    PPLX_API_KEY=sk-xxxxxxx...
    ```

### Using the Web Interface

Launch the web app:

    python main.py --mock


Then open your browser to the displayed local URL (typically http://127.0.0.1:5001).

### Using the Command Line Interface (optional, if implemented)

Use mock HTML (file upload) mode

    python main.py --mock
OR use live wiki scraping (if supported by site)

    python main.py --url "https://en.wikipedia.org/wiki/Aloy"


---

## 🧠 How It Works

This bot uses a Retrieval-Augmented Generation (RAG) pipeline tailored for Wiki/biographical data:

1. **Data Extraction**: Profile HTML is scraped or loaded from file
2. **Text Processing**: Content is split into semantic nodes by section/paragraph
3. **Vector Embedding**: Nodes are embedded using open-source HuggingFace models
4. **Storage**: Embeddings are stored in a vector database for context retrieval
5. **Query & Generation**: When you ask a question or request facts, top nodes are retrieved and a Perplexity LLM generates contextually accurate responses


---

## 🧪 Customization

### Using Different LLM Models

Edit `config.py` or update environment variables to swap models or adjust generation parameters.

### Adjusting Fact/Answer Style

Tweak the prompt templates in `config.py` to modify how facts or answers are generated:

    INITIAL_FACTS_TEMPLATE = """
    You are an AI assistant that provides detailed answers based on the provided context...
    """