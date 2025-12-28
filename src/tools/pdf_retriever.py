from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


class PDFRetriever:
    def __init__(self, pdf_dir: str = "data/pdfs"):
        self.pdf_dir = Path(pdf_dir)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vectorstore = None

    def load_documents(self):
        documents = []
        for pdf_file in self.pdf_dir.glob("*.pdf"):
            loader = PyPDFLoader(str(pdf_file))
            documents.extend(loader.load())
        return documents

    def build_index(self):
        documents = self.load_documents()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100
        )
        chunks = splitter.split_documents(documents)

        self.vectorstore = FAISS.from_documents(
            chunks,
            embedding=self.embeddings
        )

    def search(self, query: str, k: int = 4):
        if self.vectorstore is None:
            self.build_index()
        return self.vectorstore.similarity_search(query, k=k)
