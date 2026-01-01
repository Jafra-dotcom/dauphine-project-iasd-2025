from agents.pdf_agent import PDFAgent
from agents.data_agent import DataAgent
from agents.web_agent import WebAgent
from agents.router import RouterAgent

print("🚀 Démarrage du système multi-agents...")

pdf_agent = PDFAgent()
data_agent = DataAgent()
web_agent = WebAgent()
router = RouterAgent()

while True:
    question = input("\n💬 Pose ta question (ou 'exit'): ")
    if question.lower() == "exit":
        break

    route = router.route(question)
    print(f"🚦 Agent sélectionné: {route}")

    if route == "PDF":
        response = pdf_agent.answer(question)
    elif route == "DATA":
        response = data_agent.answer(question)
    else:
        response = web_agent.answer(question)

    print("\n📄 Réponse:\n", response)

