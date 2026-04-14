
import os
import warnings

warnings.filterwarnings("ignore")

# SSL certs (needed on Windows for HuggingFace model download)
import certifi
os.environ.setdefault("SSL_CERT_FILE",       certifi.where())
os.environ.setdefault("REQUESTS_CA_BUNDLE",  certifi.where())
os.environ.setdefault("CURL_CA_BUNDLE",      certifi.where())

from langchain_community.vectorstores    import FAISS
from langchain_community.embeddings      import HuggingFaceEmbeddings


EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

# Retrieval parameters
MMR_K          = 4      # final docs returned to prompt
MMR_FETCH_K    = 10     # initial candidate pool before MMR filtering
MMR_LAMBDA     = 0.65   # 0 = max diversity, 1 = max relevance; 0.65 is balanced

# Index path: look relative to this file, then fall back to CWD
_THIS_DIR  = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(_THIS_DIR, "softdel_index")

_embeddings : HuggingFaceEmbeddings | None = None
_db         : FAISS | None                 = None


def initialize():
    global _embeddings, _db

    if _db is not None:
        # Already loaded — nothing to do
        return

    # ---- 1. Embeddings model ----
    print(f"[vector_store] Loading embedding model: {EMBEDDING_MODEL} ...")
    try:
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        print("[vector_store] ✅ Embedding model loaded.")
    except Exception as e:
        raise RuntimeError(f"[vector_store] Failed to load embedding model: {e}") from e

    # ---- 2. FAISS index ----
    if not os.path.isdir(INDEX_PATH):
        raise FileNotFoundError(
            f"[vector_store] Index directory not found: {INDEX_PATH}\n"
            "Run create_index.py first to build the index."
        )

    print(f"[vector_store] Loading FAISS index from: {INDEX_PATH} ...")
    try:
        _db = FAISS.load_local(
            INDEX_PATH,
            _embeddings,
            allow_dangerous_deserialization=True,   # safe — we built this index ourselves
        )
        print("[vector_store] ✅ FAISS index loaded.")
    except Exception as e:
        raise RuntimeError(f"[vector_store] Failed to load FAISS index: {e}") from e


def get_retriever():
    _ensure_loaded()

    return _db.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k":           MMR_K,
            "fetch_k":     MMR_FETCH_K,
            "lambda_mult": MMR_LAMBDA,
        },
    )


def get_db() -> FAISS:
    _ensure_loaded()
    return _db


def is_loaded() -> bool:
    """Returns True if the index is loaded and ready."""
    return _db is not None


def _ensure_loaded():
    if _db is None:
        raise RuntimeError(
            "[vector_store] Index not loaded. "
            "Call vector_store.initialize() at application startup."
        )
