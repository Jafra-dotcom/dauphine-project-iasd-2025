from pathlib import Path
import os
os.environ["OLLAMA_NO_CUDA"] = "1"
os.environ["OLLAMA_CPU"] = "1"  # Force CPU uniquement


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
PDF_DIR = DATA_DIR / "pdfs"
XLSX_DIR = DATA_DIR / "xlsx"
VECTOR_STORE_DIR = DATA_DIR / "vectorstore"

# ⬇️ MODIFIEZ CETTE LIGNE ⬇️
EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "mistral-opt"  # ← Changez "mistral" en "mistral-opt"


