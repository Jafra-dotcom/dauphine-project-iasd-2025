from langchain_ollama import OllamaLLM
from src.tools.pdf_retriever import PDFRetriever
from src.config import PDF_DIR, EMBEDDING_MODEL, LLM_MODEL
from langfuse import observe

from src.monitoring.langfuse_client import langfuse


class PDFAgent:
    def __init__(self):
        self.retriever = PDFRetriever(
            pdf_dir=PDF_DIR,
            embedding_model=EMBEDDING_MODEL
        )
        self.llm = OllamaLLM(model=LLM_MODEL, temperature=0.0)

    @observe(name="pdf_agent")
    def run(self, question: str) -> str:
        context = self.retriever.retrieve(question)

        if (
            context.strip().startswith("iPhone")
            or "€" in context
            or "budget" in context.lower()
        ):
            langfuse.create_event(
                name="pdf_direct_answer",
                input={"question": question},
                output={"response": context}
            )
            return context

        prompt = f"""
Tu es un assistant client télécom. Essayes de bien comprendre le contexte et réponds d' une  claire et précise.


CONTEXTE :
{context}

QUESTION :
{question}

RÉPONSE :
"""
        response = self.llm.invoke(prompt).strip()

        langfuse.create_event(
            name="pdf_llm_answer",
            input={"question": question},
            output={"response": response}
        )

        return response
