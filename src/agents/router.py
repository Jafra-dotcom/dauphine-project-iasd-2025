class RouterAgent:
    def route(self, question: str) -> str:
        q = question.lower()

        if any(w in q for w in [
            "paiement", "facture", "forfait", "abonnement",
            "résiliation", "roaming", "support"
        ]):
            return "PDF"

        if any(w in q for w in [
            "combien", "nombre", "total", "clients",
            "consommation", "tickets", "abonnements"
        ]):
            return "DATA"

        return "WEB"

