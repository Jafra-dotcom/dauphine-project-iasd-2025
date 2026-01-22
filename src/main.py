from src.agents.data_agent import DataAgent
from src.agents.web_agent import WebAgent
from src.agents.router import RouterAgent
from src.agents.pdf_agent import PDFAgent
from src.monitoring.langfuse_client import langfuse


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

        # CORRECTION : Utilisez start_as_current_span() comme context manager
        with langfuse.start_as_current_span(
            name="user_question",
            input={"question": question}
        ):
            route = router.route(question)

            if route == "PDF":
                response = pdf_agent.run(question)
            elif route == "DATA":
                response = data_agent.run(question)
            else:
                response = web_agent.run(question)

            langfuse.update_current_trace(output={
                "route": route,
                "response_preview": response[:200] if response else ""
            })

        print("\n📄 Réponse:\n", response)


if __name__ == "__main__":
    main()