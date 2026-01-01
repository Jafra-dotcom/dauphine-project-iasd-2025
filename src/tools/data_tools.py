import pandas as pd
from pathlib import Path

BASE_DIR = Path.cwd()
DATA_DIR = BASE_DIR / "data" / "xlsx"


class DataTools:
    def __init__(self):
        self.clients = pd.read_excel(DATA_DIR / "clients.xlsx")
        self.forfaits = pd.read_excel(DATA_DIR / "forfaits.xlsx")
        self.abonnements = pd.read_excel(DATA_DIR / "abonnements.xlsx")
        self.consommation = pd.read_excel(DATA_DIR / "consommation.xlsx")
        self.factures = pd.read_excel(DATA_DIR / "factures.xlsx")
        self.tickets = pd.read_excel(DATA_DIR / "tickets_support.xlsx")

    def get_client_by_email(self, email: str):
        return self.clients[self.clients["email"] == email]

    def get_client_abonnement(self, email: str):
        client = self.get_client_by_email(email)
        if client.empty:
            return None

        client_id = client.iloc[0]["client_id"]
        return self.abonnements[self.abonnements["client_id"] == client_id]

    def get_unpaid_invoices(self, email: str):
        client = self.get_client_by_email(email)
        if client.empty:
            return None

        client_id = client.iloc[0]["client_id"]
        return self.factures[
            (self.factures["client_id"] == client_id)
            & (self.factures["statut_paiement"] != "payée")
        ]

    def get_consumption(self, email: str):
        client = self.get_client_by_email(email)
        if client.empty:
            return None

        client_id = client.iloc[0]["client_id"]
        return self.consommation[self.consommation["client_id"] == client_id]
