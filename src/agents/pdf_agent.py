from langchain_ollama import OllamaLLM

from src.tools.pdf_retriever import PDFRetriever
from src.config import PDF_DIR, EMBEDDING_MODEL, LLM_MODEL


class PDFAgent:
    def __init__(self):
        self.retriever = PDFRetriever(
            pdf_dir=PDF_DIR,
            embedding_model=EMBEDDING_MODEL
        )

        self.llm = OllamaLLM(
            model=LLM_MODEL,
            temperature=0.0
        )

    # ------------------------------------------------------------------

    def run(self, question: str) -> str:
        context = self.retriever.retrieve(question)

        # 🔥 BYPASS LLM POUR DONNÉES DÉTERMINISTES
        if (
            context.strip().startswith("iPhone")
            or "IPHONES DANS VOTRE BUDGET" in context
            or "moins cher" in context.lower()
            or "€" in context
        ):
            return context

        # 🧠 GÉNÉRATION LLM POUR FAQ
        prompt = f"""
Tu es un assistant client télécom.
Réponds uniquement à partir du contexte ci-dessous.
Sois clair, précis et concis.

CONTEXTE :
{context}

QUESTION :
{question}

RÉPONSE :
"""
        return self.llm.invoke(prompt).strip()
