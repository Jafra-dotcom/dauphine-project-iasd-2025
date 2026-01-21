import pandas as pd
from src.config import XLSX_DIR

print("✅ LOADED data_tools.py FROM:", __file__)


class DataTools:
    def __init__(self):
        # Chargement des fichiers
        self.clients = pd.read_excel(XLSX_DIR / "clients.xlsx")
        self.abonnements = pd.read_excel(XLSX_DIR / "abonnements.xlsx")
        self.consommation = pd.read_excel(XLSX_DIR / "consommation.xlsx")
        self.factures = pd.read_excel(XLSX_DIR / "factures.xlsx")
        self.forfaits = pd.read_excel(XLSX_DIR / "forfaits.xlsx")
        self.tickets = pd.read_excel(XLSX_DIR / "tickets_support.xlsx")

    # =============================
    # 🔎 ROUTEUR PRINCIPAL
    # =============================
    def answer(self, question: str) -> str:
        q = question.lower()

        client = self._find_client(q)
        if client is None:
            return "❌ Client non trouvé dans la base."

        client_id = client["client_id"]

        # JOINTURE 1: Clients + Abonnements + Forfaits
        client_ab_forfait = pd.merge(
            self.clients[self.clients.client_id == client_id],
            pd.merge(
                self.abonnements[self.abonnements.client_id == client_id],
                self.forfaits,
                on='forfait_id',
                how='left',
                suffixes=('_ab', '_forfait')
            ),
            on='client_id',
            how='left'
        )

        # JOINTURE 2: Clients + Consommation
        client_cons = pd.merge(
            self.clients[self.clients.client_id == client_id],
            self.consommation,
            on='client_id',
            how='left'
        )

        # JOINTURE 3: Clients + Factures
        client_fac = pd.merge(
            self.clients[self.clients.client_id == client_id],
            self.factures,
            on='client_id',
            how='left'
        )

        # JOINTURE 4: Clients + Tickets
        client_tickets = pd.merge(
            self.clients[self.clients.client_id == client_id],
            self.tickets,
            on='client_id',
            how='left'
        )

        # JOINTURE 5: Abonnements + Consommation + Factures (par mois)
        ab_cons_fac = pd.merge(
            pd.merge(
                self.abonnements[self.abonnements.client_id == client_id],
                self.consommation,
                on='client_id',
                how='left',
                suffixes=('_ab', '_cons')
            ),
            self.factures,
            on=['client_id', 'mois'],
            how='left',
            suffixes=('', '_fac')
        )

        # JOINTURE 6: Consommation + Factures + Abonnements + Forfaits
        cons_fac_ab_forfait = pd.merge(
            pd.merge(
                self.consommation[self.consommation.client_id == client_id],
                self.factures,
                on=['client_id', 'mois'],
                how='left',
                suffixes=('_cons', '_fac')
            ),
            pd.merge(
                self.abonnements[self.abonnements.client_id == client_id],
                self.forfaits,
                on='forfait_id',
                how='left',
                suffixes=('_ab', '_forfait')
            ),
            on='client_id',
            how='left'
        )

        # JOINTURE 7: Tickets + Clients (pour détails complets)
        tickets_client = pd.merge(
            self.tickets[self.tickets.client_id == client_id],
            self.clients[self.clients.client_id == client_id],
            on='client_id',
            how='left'
        )

        # JOINTURE 8: Abonnements historiques (tous les abonnements du client)
        historique_abonnements = pd.merge(
            self.abonnements[self.abonnements.client_id == client_id],
            self.forfaits,
            on='forfait_id',
            how='left'
        )

        # Détection des types de questions
        if "ticket" in q or "support" in q:
            return self._reponse_tickets(tickets_client)

        if "facture" in q or "payer" in q or "paiement" in q:
            return self._reponse_factures(client_fac)

        if "consommation" in q or "data" in q or "minutes" in q or "sms" in q:
            return self._reponse_consommation(client_cons, client_ab_forfait)

        if "forfait" in q or "abonnement" in q:
            return self._reponse_forfait(client_ab_forfait, historique_abonnements)

        if "historique" in q or "tout" in q:
            return self._reponse_historique(cons_fac_ab_forfait, historique_abonnements)

        return self._reponse_resume(client_ab_forfait, client_cons, client_fac, tickets_client)

    # =============================
    # 🔍 TROUVER CLIENT
    # =============================
    def _find_client(self, q):
        for _, client in self.clients.iterrows():
            if client["nom"].lower() in q and client["prenom"].lower() in q:
                return client
        return None

    # =============================
    # 📋 RÉPONSE RÉSUMÉ (JOINTURES 1,2,3,4)
    # =============================
    def _reponse_resume(self, client_ab_forfait, client_cons, client_fac, tickets_client):
        if client_ab_forfait.empty:
            return "❌ Données client incomplètes."
        
        client_info = client_ab_forfait.iloc[0]
        
        # Info abonnement depuis jointure 1
        ab_text = "📱 Aucun forfait"
        if not client_ab_forfait.empty and 'nom_forfait_forfait' in client_ab_forfait.columns:
            nom_forfait = client_info.get('nom_forfait_forfait', client_info.get('nom_forfait_ab', 'N/A'))
            data_gb = client_info.get('data_mensuel_gb_forfait', client_info.get('data_mensuel_gb_ab', 'N/A'))
            prix = client_info.get('prix_mensuel_forfait', client_info.get('prix_mensuel_ab', 'N/A'))
            ab_text = f"📱 Forfait: {nom_forfait} ({prix}€, {data_gb}GB)"
        
        # Info consommation depuis jointure 2
        cons_text = "📊 Aucune consommation"
        if not client_cons.empty and 'data_utilise_gb' in client_cons.columns:
            last_cons = client_cons.sort_values("mois", ascending=False)
            if not last_cons.empty:
                cons = last_cons.iloc[0]
                cons_text = f"📊 Dernière conso: {cons.data_utilise_gb}GB ({cons.mois})"
        
        # Info factures depuis jointure 3
        fac_text = "🧾 Aucune facture"
        if not client_fac.empty and 'montant' in client_fac.columns:
            impayees = client_fac[client_fac.statut_paiement.str.lower() != "payée"]
            total_impaye = impayees.montant.sum() if not impayees.empty else 0
            fac_text = f"🧾 Factures: {len(client_fac)}, Impayé: {total_impaye}€"
        
        # Info tickets depuis jointure 4/7
        tickets_text = "🎫 Aucun ticket"
        if not tickets_client.empty and 'ticket_id' in tickets_client.columns:
            ouverts = tickets_client[tickets_client.statut.str.lower() != "résolu"]
            tickets_text = f"🎫 Tickets: {len(tickets_client)}, Ouverts: {len(ouverts)}"
        
        return (
            f"👤 CLIENT: {client_info.prenom} {client_info.nom}\n"
            f"📧 {client_info.email}\n"
            f"{ab_text}\n"
            f"{cons_text}\n"
            f"{fac_text}\n"
            f"{tickets_text}"
        )

    # =============================
    # 📱 RÉPONSE FORFAIT (JOINTURES 1,8)
    # =============================
    def _reponse_forfait(self, client_ab_forfait, historique_abonnements):
        if client_ab_forfait.empty:
            return "📱 Aucun abonnement."
        
        client_info = client_ab_forfait.iloc[0]
        
        # Info forfait actuel depuis jointure 1
        nom_forfait = client_info.get('nom_forfait_forfait', client_info.get('nom_forfait_ab', 'N/A'))
        data_gb = client_info.get('data_mensuel_gb_forfait', client_info.get('data_mensuel_gb_ab', 'N/A'))
        prix = client_info.get('prix_mensuel_forfait', client_info.get('prix_mensuel_ab', 'N/A'))
        minutes = client_info.get('minutes_incluses', 'N/A')
        sms = client_info.get('sms_inclus', 'N/A')
        engagement = client_info.get('engagement_mois', 'N/A')
        
        # Historique des forfaits depuis jointure 8
        historique_text = ""
        if not historique_abonnements.empty:
            hist_list = []
            for _, row in historique_abonnements.iterrows():
                hist_list.append(f"• {row.nom_forfait_y if 'nom_forfait_y' in row else row.nom_forfait_x}")
            if hist_list:
                historique_text = f"\n📜 Historique: {', '.join(hist_list)}"
        
        return (
            f"📱 FORFAIT ACTUEL\n"
            f"• Nom: {nom_forfait}\n"
            f"• Data: {data_gb} GB\n"
            f"• Minutes: {minutes}\n"
            f"• SMS: {sms}\n"
            f"• Prix: {prix} €\n"
            f"• Engagement: {engagement} mois"
            f"{historique_text}"
        )

    # =============================
    # 📊 RÉPONSE CONSOMMATION (JOINTURES 2,1)
    # =============================
    def _reponse_consommation(self, client_cons, client_ab_forfait):
        if client_cons.empty or 'data_utilise_gb' not in client_cons.columns:
            return "📊 Aucune consommation."
        
        # Dernière consommation depuis jointure 2
        last_cons = client_cons.sort_values("mois", ascending=False).iloc[0]
        
        # Data restante depuis jointure 1
        data_restante = ""
        if not client_ab_forfait.empty:
            client_info = client_ab_forfait.iloc[0]
            data_mensuel = client_info.get('data_mensuel_gb_forfait', client_info.get('data_mensuel_gb_ab', 0))
            if isinstance(data_mensuel, (int, float)):
                data_restante = f"\n• Data restante: {max(0, data_mensuel - last_cons.data_utilise_gb):.1f} GB"
        
        # Historique 3 derniers mois
        historique = client_cons.sort_values("mois", ascending=False).head(3)
        hist_text = "\n📜 3 derniers mois:"
        for _, row in historique.iterrows():
            hist_text += f"\n• {row.mois}: {row.data_utilise_gb}GB"
        
        return (
            f"📊 CONSOMMATION ({last_cons.mois})\n"
            f"• Data: {last_cons.data_utilise_gb} GB\n"
            f"• Minutes: {last_cons.minutes_utilisees}\n"
            f"• SMS: {last_cons.sms_utilises}"
            f"{data_restante}"
            f"{hist_text}"
        )

    # =============================
    # 🧾 RÉPONSE FACTURES (JOINTURE 3)
    # =============================
    def _reponse_factures(self, client_fac):
        if client_fac.empty or 'montant' not in client_fac.columns:
            return "🧾 Aucune facture."
        
        # Calculs depuis jointure 3
        impayees = client_fac[client_fac.statut_paiement.str.lower() != "payée"]
        total_impaye = impayees.montant.sum() if not impayees.empty else 0
        
        # Dernières factures
        dernieres = client_fac.sort_values("mois", ascending=False).head(3)
        details = "\n📋 Dernières factures:"
        for _, row in dernieres.iterrows():
            details += f"\n• {row.mois}: {row.montant}€ ({row.statut_paiement})"
        
        return (
            f"🧾 FACTURES\n"
            f"• Total: {len(client_fac)}\n"
            f"• Impayées: {len(impayees)}\n"
            f"• Montant impayé: {total_impaye} €"
            f"{details}"
        )

    # =============================
    # 🎫 RÉPONSE TICKETS (JOINTURE 7)
    # =============================
    def _reponse_tickets(self, tickets_client):
        if tickets_client.empty or 'ticket_id' not in tickets_client.columns:
            return "🎫 Aucun ticket."
        
        # Tickets ouverts depuis jointure 7
        ouverts = tickets_client[tickets_client.statut.str.lower() != "résolu"]
        
        if ouverts.empty:
            return "🎫 Tous tickets résolus."
        
        tickets_list = []
        for _, row in ouverts.iterrows():
            tickets_list.append(f"• #{row.ticket_id}: {row.sujet} ({row.categorie})")
        
        return f"🎫 TICKETS OUVERTS ({len(ouverts)}):\n" + "\n".join(tickets_list[:5])

    # =============================
    # 📜 RÉPONSE HISTORIQUE (JOINTURES 6,8)
    # =============================
    def _reponse_historique(self, cons_fac_ab_forfait, historique_abonnements):
        if cons_fac_ab_forfait.empty:
            return "📜 Aucun historique."
        
        # Trier par mois
        historique = cons_fac_ab_forfait.sort_values("mois", ascending=False).head(6)
        
        lignes = []
        for _, row in historique.iterrows():
            ligne = f"• {row.mois}:"
            if 'data_utilise_gb' in row and pd.notna(row.data_utilise_gb):
                ligne += f" {row.data_utilise_gb}GB data"
            if 'montant' in row and pd.notna(row.montant):
                ligne += f", {row.montant}€"
            if 'nom_forfait_forfait' in row and pd.notna(row.nom_forfait_forfait):
                ligne += f", forfait: {row.nom_forfait_forfait}"
            lignes.append(ligne)
        
        return "📜 HISTORIQUE (6 derniers mois):\n" + "\n".join(lignes)