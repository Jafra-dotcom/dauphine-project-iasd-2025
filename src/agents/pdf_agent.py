from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

DATA_DIR = Path("data/pdfs")
VECTOR_DIR = Path("data/vectorstore")


class PDFAgent:
    def __init__(self):
        print("📄 Initialisation PDFAgent...")

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        if VECTOR_DIR.exists():
            print("📁 Chargement du vectorstore PDF...")
            self.vectorstore = FAISS.load_local(
                VECTOR_DIR, self.embeddings, allow_dangerous_deserialization=True
            )
        else:
            self.vectorstore = self._build_index()

        self.llm = OllamaLLM(model="mistral", temperature=0)

        self.prompt = ChatPromptTemplate.from_template("""
Tu es un agent de support télécom.
Réponds UNIQUEMENT à partir du contexte fourni.
Si l'information n'est pas présente, dis-le clairement.

Contexte:
{context}

Question:
{question}

Réponse:
""")

        print("✅ PDFAgent prêt")

    def _build_index(self):
        docs = []
        for pdf in DATA_DIR.glob("*.pdf"):
            print(f"📄 Chargement {pdf.name}")
            loader = PyPDFLoader(str(pdf))
            docs.extend(loader.load())

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100
        )
        chunks = splitter.split_documents(docs)

        vectorstore = FAISS.from_documents(chunks, self.embeddings)
        VECTOR_DIR.mkdir(parents=True, exist_ok=True)
        vectorstore.save_local(VECTOR_DIR)

        return vectorstore

    def answer(self, question: str) -> str:
        docs = self.vectorstore.similarity_search(question, k=4)
        context = "\n\n".join(d.page_content for d in docs)

        prompt = self.prompt.format(
            context=context,
            question=question
        )
        return self.llm.invoke(prompt)
