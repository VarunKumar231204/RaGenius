# ==============================
# IMPORTS
# ==============================

import os
import uuid
import re
import chromadb

from langchain_core.documents import Document
from langchain_community.document_loaders.text import TextLoader
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq

from sentence_transformers import SentenceTransformer


# ==============================
# LOAD TEXT FILE
# ==============================

loader = TextLoader(
    "data/python.txt",
    encoding="utf-8"
)

document = loader.load()


# ==============================
# LOAD ALL PDF FILES
# ==============================

def load_all_pdfs():

    folder_path = "data/PDFs"

    num_docs = 0
    all_docs = []

    for filename in os.listdir(folder_path):

        if filename.lower().endswith(".pdf"):

            pdf_path = os.path.join(folder_path, filename)

            loader = PyPDFLoader(pdf_path)

            doc = loader.load()

            all_docs.extend(doc)

            num_docs += 1

    print("Total PDFs are :", num_docs)
    print("Total Pages are :", len(all_docs))

    return all_docs


all_pdf_documents = load_all_pdfs()

print(type(all_pdf_documents[0]))


# ==============================
# SPLIT DOCUMENTS INTO CHUNKS
# ==============================

def split_docs(documents, chunk_size=1200, chunk_overlap=500):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    return text_splitter.split_documents(documents)


chunks = split_docs(all_pdf_documents)

print("Total Chunks :", len(chunks))


# ==============================
# EMBEDDING MANAGER
# ==============================

class EmbeddingManager:

    def __init__(self, model_name="all-MiniLM-L6-v2"):

        print("Loading model ......", model_name)

        self.model = SentenceTransformer(model_name)

        print(
            "Embedding dimensions :",
            self.model.get_sentence_embedding_dimension()
        )

    def generate_embeddings(self, text):

        embeddings = self.model.encode(
            text,
            show_progress_bar=True
        )

        print("Embeddings shape :", embeddings.shape)

        return embeddings


embedding_manager = EmbeddingManager()


# ==============================
# VECTOR STORE MANAGER
# ==============================

class VectorStoreManager:

    def __init__(
        self,
        persist_directory="data/vector_store",
        collection_name="pdf_documents"
    ):

        self.collection_name = collection_name
        self.persist_directory = persist_directory

        self._initialize_store()

    def _initialize_store(self):

        os.makedirs(self.persist_directory, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=self.persist_directory
        )

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={
                "description": "vector store collection for pdf embeddings in RAG"
            }
        )

        print("Initialized vector store:", self.collection_name)
        print("Docs in collection:", self.collection.count())

    def add_documents(self, documents, embeddings):

        if len(documents) != len(embeddings):
            raise ValueError("Mismatch between docs and embeddings")

        ids = []
        metadatas = []
        docs = []
        embeds = []

        for i, (doc, emb) in enumerate(zip(documents, embeddings)):

            ids.append(f"doc_{uuid.uuid4()}")

            metadata = dict(doc.metadata)
            metadata["doc_index"] = i
            metadata["content_length"] = len(doc.page_content)

            metadatas.append(metadata)
            docs.append(doc.page_content)
            embeds.append(emb.tolist())

        self.collection.add(
            ids=ids,
            metadatas=metadatas,
            documents=docs,
            embeddings=embeds
        )

        print("Total documents added =", len(docs))
        print("Docs in collection:", self.collection.count())


vector_store = VectorStoreManager()


# ==============================
# PIPELINE
# ==============================

texts = [doc.page_content for doc in chunks]

embeddings = embedding_manager.generate_embeddings(texts)

vector_store.add_documents(chunks, embeddings)


# ==============================
# RAG RETRIEVER
# ==============================

class RAGRetriever:

    def __init__(self, embedding_manager, vector_store):

        self.embedding_manager = embedding_manager
        self.vector_store = vector_store

    def retrieve(self, query, top_k=5, score_threshold=0.0):

        query_embedding = self.embedding_manager.generate_embeddings([query])[0]

        results = self.vector_store.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )

        retrieved_docs = []

        if results["documents"] and results["documents"][0]:

            for i, (doc_id, metadata, document, distance) in enumerate(zip(
                results["ids"][0],
                results["metadatas"][0],
                results["documents"][0],
                results["distances"][0]
            )):

                similarity = 1 - distance

                if similarity >= score_threshold:

                    retrieved_docs.append({
                        "id": doc_id,
                        "document": document,
                        "metadata": metadata,
                        "distance": distance,
                        "similarity_score": similarity,
                        "rank": i + 1
                    })

        return retrieved_docs


rag_retriever = RAGRetriever(embedding_manager, vector_store)


# ==============================
# GROQ LLM
# ==============================

API_Key_Groq = "enter your api key here"

llm = ChatGroq(
    groq_api_key=API_Key_Groq,
    model="qwen/qwen3-32b",
    temperature=0.1,
    max_tokens=4096
)


# ==============================
# CLEANING FUNCTION
# ==============================

def clean_response(raw_text: str) -> str:
    # Remove <think>...</think> blocks
    cleaned = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL)
    return cleaned.strip()


# ==============================
# OUTPUT GENERATION (FIXED)
# ==============================

def generate_output(query, retriever, llm, top_k=3):

    results = retriever.retrieve(query, top_k)

    context = "\n".join([doc["document"] for doc in results]) if results else ""

    if not context:
        print("No relevant context found")

    prompt = f"""
Use the given context to answer the question.

Context:
{context}

Question:
{query}
"""

    response = llm.invoke(prompt)

    # ✅ Clean the response before returning
    return clean_response(response.content)


# ==============================
# TEST
# ==============================

answer = generate_output("what is connectivity", rag_retriever, llm)

print(answer)
