
import os
import warnings
import certifi
from pathlib import Path
from typing import List

import pandas as pd

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
    WebBaseLoader,
)
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

warnings.filterwarnings("ignore")

os.environ["SSL_CERT_FILE"]      = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
os.environ["CURL_CA_BUNDLE"]     = certifi.where()


DOCS_DIR        = "documents"
INDEX_DIR       = "softdel_index"
URLS_FILE       = os.path.join(DOCS_DIR, "urls.txt")
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"      

# (chunk_size, chunk_overlap) per document type
CHUNK_MANUAL   = (1200, 200)   # PDFs — wide window, preserve technical context
CHUNK_FAQ_DOC  = (400,  50)   # DOCX FAQs — keep Q&A pairs together
CHUNK_WEB_TXT  = (900,  150)   # scraped website text
CHUNK_MARKDOWN = (900,  150)   # markdown docs


def load_pdfs(docs_dir: str) -> List[Document]:
    documents = []
    for f in Path(docs_dir).glob("*.pdf"):
        try:
            print(f"  📄 PDF: {f.name}")
            pages = PyPDFLoader(str(f)).load()
            for page in pages:
                page.metadata.update({"doc_type": "manual", "source": f.name})
            documents.extend(pages)
            print(f"     ✅ {len(pages)} pages")
        except Exception as e:
            print(f"     ❌ {e}")
    return documents


def load_docx(docs_dir: str) -> List[Document]:
    documents = []
    files = list(Path(docs_dir).glob("*.docx")) + list(Path(docs_dir).glob("*.doc"))
    for f in files:
        try:
            print(f"  📝 DOCX: {f.name}")
            docs = Docx2txtLoader(str(f)).load()
            for doc in docs:
                doc.metadata.update({"doc_type": "faq_doc", "source": f.name})
            documents.extend(docs)
            print(f"     ✅ Loaded")
        except Exception as e:
            print(f"     ❌ {e}")
    return documents


def load_excel(docs_dir: str) -> List[Document]:
    documents = []
    files = list(Path(docs_dir).glob("*.xlsx")) + list(Path(docs_dir).glob("*.xls"))
    for f in files:
        try:
            print(f"  📊 Excel: {f.name}")
            xl    = pd.ExcelFile(f)
            total = 0
            for sheet in xl.sheet_names:
                try:
                    df = xl.parse(sheet).dropna(how="all").fillna("")
                    df.columns = [str(c).strip() for c in df.columns]
                    for _, row in df.iterrows():
                        parts = [
                            f"{col}: {str(row[col]).strip()}"
                            for col in df.columns
                            if str(row[col]).strip()
                            and str(row[col]).strip().lower() not in ("nan", "none")
                        ]
                        if parts:
                            documents.append(Document(
                                page_content=" | ".join(parts),
                                metadata={"doc_type": "faq", "source": f.name, "sheet": sheet}
                            ))
                            total += 1
                except Exception as se:
                    print(f"     ⚠️  Sheet '{sheet}': {se}")
            print(f"     ✅ {total} rows across {len(xl.sheet_names)} sheet(s)")
        except Exception as e:
            print(f"     ❌ {e}")
    return documents


def load_csv(docs_dir: str) -> List[Document]:
    documents = []
    for f in Path(docs_dir).glob("*.csv"):
        try:
            print(f"  📊 CSV: {f.name}")
            try:
                df = pd.read_csv(f, encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(f, encoding="latin1")

            df = df.dropna(how="all").fillna("")
            df.columns = [str(c).strip() for c in df.columns]
            count = 0
            for _, row in df.iterrows():
                parts = [
                    f"{col}: {str(row[col]).strip()}"
                    for col in df.columns
                    if str(row[col]).strip()
                    and str(row[col]).strip().lower() not in ("nan", "none")
                ]
                if parts:
                    documents.append(Document(
                        page_content=" | ".join(parts),
                        metadata={"doc_type": "faq", "source": f.name}
                    ))
                    count += 1
            print(f"     ✅ {count} rows")
        except Exception as e:
            print(f"     ❌ {e}")
    return documents


def load_txt(docs_dir: str) -> List[Document]:
    documents = []
    for f in Path(docs_dir).glob("*.txt"):
        if f.name.lower() == "urls.txt":
            continue
        try:
            print(f"  📃 TXT: {f.name}")
            docs = _try_load_text(str(f))
            for doc in docs:
                doc.metadata.update({"doc_type": "web", "source": f.name})
            documents.extend(docs)
            print(f"     ✅ Loaded")
        except Exception as e:
            print(f"     ❌ {e}")
    return documents


def load_markdown(docs_dir: str) -> List[Document]:
    documents = []
    for f in Path(docs_dir).glob("*.md"):
        try:
            print(f"  📄 MD: {f.name}")
            docs = _try_load_text(str(f))
            for doc in docs:
                doc.metadata.update({"doc_type": "doc", "source": f.name})
            documents.extend(docs)
            print(f"     ✅ Loaded")
        except Exception as e:
            print(f"     ❌ {e}")
    return documents


def load_urls(urls_file: str) -> List[Document]:
    documents = []
    if not os.path.exists(urls_file):
        return documents
    with open(urls_file, "r", encoding="utf-8") as fh:
        urls = [
            line.strip() for line in fh
            if line.strip() and not line.strip().startswith("#")
        ]
    if not urls:
        return documents
    print(f"  🌐 Loading {len(urls)} URL(s)...")
    for url in urls:
        try:
            print(f"     → {url}")
            docs = WebBaseLoader(url).load()
            for doc in docs:
                doc.metadata.update({"doc_type": "web", "source": url})
            documents.extend(docs)
            print(f"       ✅ Loaded")
        except Exception as e:
            print(f"       ❌ {e}")
    return documents


def _try_load_text(path: str) -> List[Document]:
    """Try utf-8, fall back to latin1."""
    try:
        return TextLoader(path, encoding="utf-8").load()
    except UnicodeDecodeError:
        return TextLoader(path, encoding="latin1").load()

def _splitter(size: int, overlap: int) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )


def split_by_type(documents: List[Document]) -> List[Document]:
    groups: dict[str, List[Document]] = {}
    for doc in documents:
        dt = doc.metadata.get("doc_type", "default")
        groups.setdefault(dt, []).append(doc)

    chunks: List[Document] = []

    for doc_type, docs in groups.items():
        if doc_type == "faq":
            chunks.extend(docs)
            print(f"  ✂️  FAQ ({doc_type}): {len(docs)} rows → kept as-is")

        elif doc_type == "manual":
            split = _splitter(*CHUNK_MANUAL).split_documents(docs)
            chunks.extend(split)
            print(f"  ✂️  Manuals: {len(docs)} pages → {len(split)} chunks")

        elif doc_type == "web":
            split = _splitter(*CHUNK_WEB_TXT).split_documents(docs)
            chunks.extend(split)
            print(f"  ✂️  Web/TXT: {len(docs)} docs → {len(split)} chunks")

        elif doc_type == "doc":
            split = _splitter(*CHUNK_MARKDOWN).split_documents(docs)
            chunks.extend(split)
            print(f"  ✂️  Markdown: {len(docs)} docs → {len(split)} chunks")
        elif doc_type == "faq_doc":
            # DOCX FAQ — small chunks to keep each Q&A atomic
            splitter = _splitter(400, 30)
            split = splitter.split_documents(docs)
            chunks.extend(split)
            print(f"  ✂️  FAQ DOCX: {len(docs)} docs → {len(split)} chunks")
        else:
            split = _splitter(*CHUNK_WEB_TXT).split_documents(docs)
            chunks.extend(split)
            print(f"  ✂️  Other: {len(docs)} docs → {len(split)} chunks")

    return chunks

def build_index(chunks: List[Document]) -> FAISS:
    print(f"\n🔄 Loading embedding model: {EMBEDDING_MODEL}")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    print(f"🔄 Embedding {len(chunks)} chunks and building FAISS index...")
    db = FAISS.from_documents(chunks, embeddings)
    db.save_local(INDEX_DIR)
    print(f"✅ Index saved → {INDEX_DIR}/")
    return db


def main():
    print("=" * 65)
    print("  Softdel VA — Document Indexer")
    print("=" * 65)

    os.makedirs(DOCS_DIR, exist_ok=True)

    print("\n📚 Loading documents...\n")
    all_docs: List[Document] = []
    all_docs.extend(load_pdfs(DOCS_DIR))
    all_docs.extend(load_docx(DOCS_DIR))
    all_docs.extend(load_excel(DOCS_DIR))
    all_docs.extend(load_csv(DOCS_DIR))
    all_docs.extend(load_txt(DOCS_DIR))
    all_docs.extend(load_markdown(DOCS_DIR))
    all_docs.extend(load_urls(URLS_FILE))

    print(f"\n{'─'*65}")
    print(f"📊 Total raw documents loaded: {len(all_docs)}")

    if not all_docs:
        print("\n⚠️  No documents found. Add files to documents/ and retry.")
        return

    print(f"\n✂️  Splitting...\n")
    chunks = split_by_type(all_docs)

    # Drop empty
    chunks = [c for c in chunks if c.page_content.strip()]
    print(f"\n📦 Final chunk count: {len(chunks)}")

    db = build_index(chunks)

    print("\n🧪 Smoke test...")
    try:
        results = db.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 3, "fetch_k": 8, "lambda_mult": 0.65}
        ).invoke("What is Softdel?")
        print(f"✅ Retrieved {len(results)} chunks")
        print(f"   Sample: {results[0].page_content[:120].strip()}...")
    except Exception as e:
        print(f"⚠️  Smoke test failed: {e}")

    print("\n" + "=" * 65)
    print("✅ INDEXING COMPLETE")
    print("=" * 65)
    print(f"  Documents loaded : {len(all_docs)}")
    print(f"  Chunks indexed   : {len(chunks)}")
    print(f"  Embedding model  : {EMBEDDING_MODEL}")
    print(f"  Index path       : {INDEX_DIR}/")
    print(f"\n🚀 Start the app: python main.py")
    print("=" * 65)


if __name__ == "__main__":
    main()
