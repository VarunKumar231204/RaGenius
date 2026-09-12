from flask import Flask, render_template, request, jsonify, session
from Rag_Pipeline import rag_retriever, llm, embedding_manager, vector_store
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for session storage

# =========================
# CLEANING FUNCTION
# =========================
def clean_response(raw_text: str) -> str:
    cleaned = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL)
    return cleaned.strip()

# =========================
# HOME ROUTE (Landing Page)
# =========================
@app.route("/")
def home():
    return render_template("index.html")

# =========================
# LOGIN PAGE ROUTE
# =========================
@app.route("/login")
def login():
    return render_template("login.html")

# =========================
# CHAT PAGE ROUTE
# =========================
@app.route("/chat_page")
def chat_page():
    return render_template("chat.html")

# =========================
# CHAT API ROUTE (Text Only)
# =========================
@app.route("/chat_api", methods=["POST"])
def chat_api():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"response": "No message provided."})

    user_query = data["message"]

    # Retrieve relevant documents
    retrieved_docs = rag_retriever.retrieve(user_query, top_k=3)

    # Build context (fallback if no docs found)
    context = "\n\n".join([doc["document"] for doc in retrieved_docs]) if retrieved_docs else "No relevant context found in knowledge base."

    # Improved Prompt with formatting instructions
    prompt = f"""
You are an AI assistant. 
Make sure answers are detailed and understandable.
Use:
- Use headings (###) for sections
- give answers in an good format not like an gimicky format
- Use bullet points (•) for lists
- Add emojis for readability
- Always include a short summary at the end
- Give answers in an good font style not an robotic like font
- please give answers to only that queries only which are related to available pdfs chunks and documents otherwise return only one sentence which is No relevant context found in knowledge base.
- strictly only answer those questions which are related to the pdf chunks.
- donot answer any other questions which are not related to the pdf chunks.
- Respond strictly in the style requested by the user:
     - "definition" → Only give the definition in 1–2 sentences.
     - "short answer" → Concise, 2–3 sentences max.
     - "detailed answer" → Full explanation with headings and bullet points.
     - "very detailed answer" → Extended explanation with examples, comparisons, and structured sections.
     - "interview style" → Q&A format with clear separation of question and answer.
     - please give answers to only that queries only which are related to available pdfs chunks and documents otherwise return only one sentence which is No relevant context found in knowledge base.

Context:
{context}

Question:
{user_query}

Answer:
"""
    response = llm.invoke(prompt)
    final_response = clean_response(response.content)

    print("\n" + "=" * 80)
    print("QUESTION:", user_query)
    print("=" * 80)
    print("ANSWER:")
    print(final_response)
    print("=" * 80)

    # HISTORY TRACKING (last 3 chats)
    if "chat_history" not in session:
        session["chat_history"] = []
    session["chat_history"].append(user_query)
    session["chat_history"] = session["chat_history"][-3:]

    return jsonify({
        "response": final_response,
        "history": session["chat_history"]
    })

# =========================
# PDF UPLOAD ROUTE
# =========================
@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    file = request.files.get("file")
    if not file:
        return jsonify({"response": "No file uploaded."})

    os.makedirs("./data/pdfs", exist_ok=True)
    filepath = f"./data/pdfs/{file.filename}"
    file.save(filepath)

    # Load PDF
    loader = PyPDFLoader(filepath)
    docs = loader.load()

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=500)
    chunks = splitter.split_documents(docs)

    # Ensure metadata uses actual PDF page numbers
    for chunk in chunks:
        chunk.metadata["source"] = os.path.basename(filepath)

    # Generate embeddings
    texts = [doc.page_content for doc in chunks]
    embeddings = embedding_manager.generate_embeddings(texts)

    # Add to vector store
    vector_store.add_documents(chunks, embeddings)

    return jsonify({
        "response": f"PDF '{file.filename}' uploaded, processed, and added to knowledge base."
    })

# =========================
# KNOWLEDGE BASE ROUTE
# =========================
@app.route("/knowledge_base")
def knowledge_base():
    pdf_folder = "./data/pdfs"
    pdf_files = []
    if os.path.exists(pdf_folder):
        for fname in os.listdir(pdf_folder):
            fpath = os.path.join(pdf_folder, fname)
            if os.path.isfile(fpath) and fname.lower().endswith(".pdf"):
                stats = os.stat(fpath)
                pdf_files.append({
                    "name": fname,
                    "size_kb": round(stats.st_size / 1024, 2),
                    "uploaded": datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                })

    model_info = {
        "Model": "Groq LLM (qwen/qwen3-32b)",
        "Retriever": "ChromaDB Vector Store",
        "Embedding": "SentenceTransformer",
        "Pipeline": "Retrieval-Augmented Generation (RAG)"
    }

    return render_template("knowledge_base.html", pdfs=pdf_files, model_info=model_info)

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
