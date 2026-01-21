from langchain_ollama import OllamaLLM


class WebAgent:
    def __init__(self):
        print("🌐 Initialisation WebAgent...")
        self.llm = OllamaLLM(model="mistral-opt", temperature=0)
        print("✅ WebAgent prêt")

    def run(self, question: str) -> str:
        prompt = f"""
Tu es un assistant généraliste.
Réponds de manière claire et concise.

Question:
{question}

Réponse:
"""
        return self.llm.invoke(prompt)




