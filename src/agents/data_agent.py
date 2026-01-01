from pathlib import Path
import pandas as pd
from langchain_ollama import OllamaLLM

DATA_DIR = Path("data/xlsx")


class DataAgent:
    def __init__(self):
        print("📊 Initialisation DataAgent...")

        self.tables = {}
        for file in DATA_DIR.glob("*.xlsx"):
            self.tables[file.stem] = pd.read_excel(file)
            print(f"📁 Chargé: {file.name}")

        self.llm = OllamaLLM(model="mistral", temperature=0)
        print("✅ DataAgent prêt")

    def _build_context(self) -> str:
        context = ""
        for name, df in self.tables.items():
            context += f"\n### Table: {name}\n"
            context += f"Colonnes: {list(df.columns)}\n"
            context += df.head(5).to_string(index=False)
            context += "\n"
        return context

    def answer(self, question: str) -> str:
        print(f"❓ Question DATA: {question}")

        if not self.tables:
            return "❌ Aucune donnée Excel disponible."

        context = self._build_context()

        prompt = f"""
Tu es un analyste de données.
Tu réponds UNIQUEMENT à partir des tableaux ci-dessous.
Si la réponse n'est pas déductible, dis-le clairement.

Données:
{context}

Question:
{question}

Réponse:
"""
        return self.llm.invoke(prompt)
