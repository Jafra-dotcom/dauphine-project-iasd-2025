"""Main module for the TelecomPlus multi-agent support system."""


from agents.router import RouterAgent


if __name__ == "__main__":
    router = RouterAgent()

    questions = [
        "Quels sont vos modes de paiement ?",
        "Quelle est ma consommation ce mois-ci ?",
        "Bonjour"
    ]

    for q in questions:
        print(q, "->", router.route(q))


