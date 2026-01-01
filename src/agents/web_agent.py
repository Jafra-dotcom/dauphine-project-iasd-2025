from langchain_ollama import OllamaLLM

class WebAgent:
    def __init__(self):
        self.llm = OllamaLLM(model="mistral", temperature=0)

    def answer(self, question: str) -> str:
        prompt = f"""
Réponds de manière générale et concise à la question suivante:

{question}
"""
        return self.llm.invoke(prompt)



