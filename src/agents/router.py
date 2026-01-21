import pandas as pd
from src.config import XLSX_DIR

class RouterAgent:
    def __init__(self):
        # Charger les clients une fois au démarrage
        self.client_names = self._load_client_names()
    
    def _load_client_names(self):
        """Charge tous les noms/prénoms des clients depuis Excel"""
        try:
            clients_df = pd.read_excel(XLSX_DIR / "clients.xlsx")
            names = []
            
            # Ajouter les combinaisons nom/prénom
            for _, row in clients_df.iterrows():
                if pd.notna(row.get('nom')) and pd.notna(row.get('prenom')):
                    full_name = f"{row['prenom']} {row['nom']}".lower()
                    names.append(full_name)
                    # Ajouter aussi séparément pour plus de robustesse
                    names.append(row['nom'].lower())
                    names.append(row['prenom'].lower())
            
            return list(set(names))  # Supprimer les doublons
            
        except Exception as e:
            print(f"⚠️ Erreur chargement clients: {e}")
            return []
    
    def route(self, question: str) -> str:
        q = question.lower().strip()
        
        # 1. Vérifier si la question contient un nom de client
        for name in self.client_names:
            if name in q:
                return "DATA"
        
        # 2. Vérifier pattern "Je m'appelle [Prénom] [Nom]"
        if "je m'appelle" in q or "m'appelle" in q:
            # Extraire le nom après "je m'appelle"
            parts = q.split("je m'appelle")
            if len(parts) > 1:
                potential_name = parts[1].strip().split()[0] if parts[1].strip() else ""
                if potential_name:
                    return "DATA"
        
        # 3. Questions iPhone, prix, catalogue → PDF
        iphone_keywords = ["iphone", "téléphone", "smartphone", "appareil"]
        price_keywords = ["prix", "coûte", "combien", "€", "euro", "budget", "tarif"]
        catalog_keywords = ["catalogue", "modèle", "128gb", "256gb", "512gb", "1tb", "disponible"]
        
        if any(kw in q for kw in iphone_keywords + price_keywords + catalog_keywords):
            return "PDF"
        
        # 4. FAQs, procédures, comment faire → PDF
        procedure_keywords = [
            "comment", "activer", "configurer", "désactiver", "paramétrer",
            "pourquoi", "quels", "quelles", "quel", "quelle", "que faire",
            "procédure", "étape", "guide", "tutoriel", "faire", "résilier",
            "souscrire", "abonner", "changer", "modifier", "mettre à jour"
        ]
        
        if any(kw in q for kw in procedure_keywords):
            return "PDF"
        
        # 5. Questions techniques, support → PDF
        tech_keywords = [
            "mms", "sms", "roaming", "internet", "data", "réseau",
            "forfait", "abonnement", "facture", "paiement", "mobile",
            "téléphonie", "support", "assistance", "aide", "service"
        ]
        
        if any(kw in q for kw in tech_keywords):
            return "PDF"
        
        # 6. Statistiques, comptes, listes → DATA
        data_keywords = [
            "combien de", "nombre de", "total de", "quantité de",
            "statistique", "moyenne", "minimum", "maximum", "liste",
            "tous les", "chaque", "par", "groupé", "trié", "filtré",
            "client", "clients", "abonné", "abonnés", "utilisateur"
        ]
        
        if any(kw in q for kw in data_keywords):
            return "DATA"
        
        # 7. Par défaut: WEB
        return "WEB"