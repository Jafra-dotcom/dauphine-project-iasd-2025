from langchain_ollama import OllamaLLM
from langfuse import observe



class WebAgent:
    def __init__(self):
        print("🌐 Initialisation WebAgent...")
        self.llm = OllamaLLM(model="mistral-opt", temperature=0)
        print("✅ WebAgent prêt")

    @observe(name="web_agent")
    def run(self, question: str) -> str:
        prompt = f"""
Tu es un assistant généraliste.
Réponds clairement et brièvement.

QUESTION:
{question}

RÉPONSE:
"""
        return self.llm.invoke(prompt)




