# 🤖 RAGenius — RAG-Based Document Intelligence System

**RAGenius** is a Retrieval-Augmented Generation (RAG) based document intelligence system that allows users to upload PDF documents and ask questions about their content using natural language.

Instead of relying only on an LLM's pre-trained knowledge, RAGenius retrieves the most relevant information from the uploaded documents and provides **context-aware answers** based on that information.

---

## 📌 Overview

Large Language Models can generate impressive responses, but they may not have access to information contained in private or newly uploaded documents.

RAGenius solves this problem using a **Retrieval-Augmented Generation pipeline**:

```text
                ┌──────────────────┐
                │    PDF Upload    │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │  PDF Text/Image  │
                │    Extraction    │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │  Text Chunking   │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │   Embeddings     │
                │ MiniLM-L6-v2     │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ ChromaDB Vector  │
                │      Store       │
                └────────┬─────────┘
                         │
                User Question
                         │
                         ▼
                ┌──────────────────┐
                │ Similarity Search│
                │    Top-K = 3     │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Retrieved Context│
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │    Groq LLM      │
                │   Qwen3-32B      │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │ Context-Aware    │
                │      Answer      │
                └──────────────────┘
```

---

## ✨ Features

* 📄 Upload and process PDF documents
* 🔎 Semantic search using vector embeddings
* 🧠 Retrieval-Augmented Generation pipeline
* 💬 Natural-language question answering
* 📚 Persistent document knowledge base using ChromaDB
* ⚡ Fast LLM inference through Groq
* 🔐 Login-based application interface
* 🖼️ PDF image extraction support
* 💾 Stores document metadata such as page number and source
* 🧹 Cleans unnecessary LLM reasoning/output before displaying responses
* 🗂️ Supports multiple documents in the knowledge base
* 🌐 Flask-based web interface

---

## 🛠️ Tech Stack

| Technology                | Purpose                              |
| ------------------------- | ------------------------------------ |
| **Python**                | Core programming language            |
| **Flask**                 | Backend web framework                |
| **LangChain**             | RAG pipeline and document processing |
| **ChromaDB**              | Vector database                      |
| **Sentence Transformers** | Text embeddings                      |
| **all-MiniLM-L6-v2**      | Embedding model                      |
| **Groq**                  | LLM inference                        |
| **Qwen3-32B**             | Generative language model            |
| **PyMuPDF**               | PDF/image processing                 |
| **HTML/CSS/JavaScript**   | Frontend                             |
| **Bootstrap**             | UI components                        |

---

# 🔄 RAG Pipeline

RAGenius follows a two-stage architecture:

### 1. Document Ingestion

When a PDF is uploaded:

```text
PDF
 ↓
Text Extraction
 ↓
Text Splitting
 ↓
Embedding Generation
 ↓
ChromaDB
```

The document is divided into smaller chunks using a recursive text splitter.

Current configuration:

```text
Chunk Size       : 1200
Chunk Overlap    : 500
Embedding Model  : all-MiniLM-L6-v2
Vector Database  : ChromaDB
```

The overlap between chunks helps preserve contextual information that may otherwise be lost at chunk boundaries.

---

### 2. Question Answering

When a user asks a question:

```text
User Question
      ↓
Question Embedding
      ↓
ChromaDB Similarity Search
      ↓
Top 3 Relevant Chunks
      ↓
Context + Question
      ↓
Qwen3-32B
      ↓
Generated Answer
```

The retrieved document chunks are supplied to the LLM as context so that the generated response is grounded in the uploaded documents.

---

# 🧩 Architecture

```text
                         RAGenius
                            │
             ┌──────────────┴──────────────┐
             │                             │
       Document Flow                 Query Flow
             │                             │
             ▼                             ▼
       PDF Upload                    User Question
             │                             │
             ▼                             ▼
       PyMuPDF /                     Embedding
       PyPDFLoader                       │
             │                           ▼
             ▼                      ChromaDB
       Text Chunking                     │
             │                           ▼
             ▼                     Top-K Retrieval
       Sentence                            │
       Transformer                         │
             │                             ▼
             ▼                       Context + Query
       ChromaDB                            │
             │                             ▼
             └──────────────────────► Groq
                                       │
                                       ▼
                                  Qwen3-32B
                                       │
                                       ▼
                                     Answer
```

---

# 📁 Project Structure

```text
RAGenius/
│
├── app.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── pdfs/
│   │   └── uploaded_documents.pdf
│   │
│   └── vector_store/
│       └── chroma.sqlite3
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── chat.html
│   └── knowledge_base.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
└── Assets/
    └── Logo.png
```

> **Note:** The exact folder structure may vary depending on the current implementation.

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/VarunKumar231204/RaGenius.git
```

```bash
cd RaGenius
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

RAGenius uses Groq for LLM inference.

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

Never commit your API key to GitHub.

Add the following to `.gitignore`:

```gitignore
.env
venv/
__pycache__/
*.pyc
```

---

# ▶️ Running the Application

Start the Flask application:

```bash
python app.py
```

The application will start on the configured local Flask server.

Open the displayed local URL in your browser.

For example:

```text
http://127.0.0.1:5000
```

---

# 💬 Example Usage

### Step 1 — Login

Access the RAGenius web application and log in.

### Step 2 — Upload a PDF

Upload a document such as:

* Research paper
* Academic notes
* Technical documentation
* Project report
* E-book
* Company document

### Step 3 — Processing

RAGenius:

1. Extracts the document content.
2. Splits the content into chunks.
3. Generates vector embeddings.
4. Stores the embeddings in ChromaDB.

### Step 4 — Ask Questions

Example:

```text
What is the main objective of this document?
```

or:

```text
Explain the methodology used in the research.
```

or:

```text
What are the key findings mentioned in the document?
```

### Step 5 — Retrieve and Generate

The system retrieves the most relevant document chunks and provides them to the LLM as context.

The LLM then generates a response based on the retrieved information.

---

# 🧠 Why RAG?

A traditional LLM-based chatbot can answer questions using its pre-trained knowledge, but it may not know the contents of a user's private document.

RAG addresses this limitation by connecting an LLM with an external knowledge source.

### Traditional LLM

```text
Question → LLM → Answer
```

### RAG

```text
Question
   ↓
Retriever
   ↓
Relevant Documents
   ↓
LLM + Retrieved Context
   ↓
Answer
```

This makes the system more suitable for **document-specific question answering**.

---

# 🔍 Retrieval Process

RAGenius uses the `all-MiniLM-L6-v2` Sentence Transformer model to convert text into numerical vector representations.

Documents with semantically similar meanings have vectors that are closer together in the embedding space.

When a question is asked:

```text
Question
   ↓
Embedding
   ↓
Vector Similarity Search
   ↓
Top 3 Relevant Chunks
```

These chunks are then passed to the language model as context.

---

# 🤖 Language Model

RAGenius uses a Qwen3-32B model through the Groq inference platform.

The retrieved context and user question are combined into a prompt so the model can generate a context-aware response.

The application also performs response cleaning to remove unwanted model reasoning/output before presenting the final answer to the user.

---

# 📄 PDF Processing

PDF documents are processed using **PyMuPDF** and LangChain's PDF loading utilities.

The system can:

* Extract text from PDF pages
* Preserve page-related metadata
* Process document content into chunks
* Extract images from PDFs
* Store document source information for retrieval

---

# 🗄️ Vector Database

**ChromaDB** is used as the vector database.

It stores:

* Document chunks
* Embeddings
* Metadata
* Source information

Example metadata:

```text
{
    "source": "document.pdf",
    "page": 5
}
```

This allows the application to associate retrieved information with its original document source.

---

# 🚀 Future Improvements

Possible future enhancements include:

* [ ] Streaming LLM responses
* [ ] Improved source/citation display
* [ ] Conversation memory
* [ ] Support for DOCX and TXT files
* [ ] Multi-user document isolation
* [ ] Hybrid keyword + semantic search
* [ ] Reranking retrieved documents
* [ ] Better hallucination detection
* [ ] OCR support for scanned PDFs
* [ ] Cloud deployment
* [ ] Authentication using a production database
* [ ] Advanced document analytics
* [ ] Evaluation using RAG-specific metrics

---

# ⚠️ Limitations

Like other RAG systems, RAGenius can be affected by:

* Poor-quality or scanned PDFs
* Incorrect text extraction
* Incomplete retrieval
* Ambiguous questions
* Insufficient document context
* LLM-generated inaccuracies

The quality of the final answer depends on both **retrieval quality** and **LLM generation quality**.

---

# 🔒 Security

Do not expose sensitive information or API keys in the repository.

Recommended `.gitignore`:

```gitignore
.env
venv/
__pycache__/
*.pyc
data/vector_store/
```

If the vector database contains private documents, it should also remain outside the public repository.

---

# 📊 Project Highlights

### RAG Pipeline

```text
PDF → Chunking → Embeddings → ChromaDB
                         ↓
Question → Retrieval → Context → Qwen3-32B → Answer
```

### Key Parameters

| Parameter           | Value            |
| ------------------- | ---------------- |
| Chunk Size          | 1200             |
| Chunk Overlap       | 500              |
| Embedding Model     | all-MiniLM-L6-v2 |
| Embedding Dimension | 384              |
| Vector Database     | ChromaDB         |
| Retrieved Chunks    | Top 3            |
| LLM                 | Qwen3-32B        |
| Backend             | Flask            |

---

# 👨‍💻 Author

**Varun Kumar**

B.Tech — Information Technology
Guru Jambheshwar University of Science and Technology (GJUST), Hisar

GitHub: **VarunKumar231204**

---

# ⭐ Acknowledgements

This project uses several open-source technologies and frameworks, including:

* Flask
* LangChain
* ChromaDB
* Sentence Transformers
* PyMuPDF
* Groq
* Qwen

---

## 📜 License

This project is intended for educational and academic purposes.

You may modify and extend the project according to your requirements.
