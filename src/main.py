from src.agents.pdf_agent import PDFAgent
from src.agents.data_agent import DataAgent
from src.agents.web_agent import WebAgent
from src.agents.router import RouterAgent


def main():
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
            response = pdf_agent.run(question)

        elif route == "DATA":
            
            response = data_agent.run(question)

        else:
            response = web_agent.run(question)

        print("\n📄 Réponse:\n", response)


if __name__ == "__main__":
    main()
