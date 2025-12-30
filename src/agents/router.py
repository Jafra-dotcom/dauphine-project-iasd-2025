import os
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class RouterAgent:
    def __init__(self):
        pass

    def route(self, question: str) -> str:
        question = question.lower()

        if any(word in question for word in ["paiement", "offre", "résiliation", "condition"]):
            return "PDF"
        elif any(word in question for word in ["facture", "consommation", "client"]):
            return "DATA"
        else:
            return "GENERAL"
