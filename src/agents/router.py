
import pandas as pd
from src.config import XLSX_DIR
from src.monitoring.langfuse_client import langfuse


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
        
        # Initialiser les métadonnées pour Langfuse
        metadata = {
            "question": question,
            "decision_steps": [],
            "matched_keywords": []
        }
        
        # Gérer Langfuse avec un fallback
        try:
            # Utiliser Langfuse si disponible
            with langfuse.start_as_current_span(
                name="router_agent",
                input={"question": question}
            ) as span:
                result = self._route_logic(q, metadata)
                span.update(output={"route": result, "metadata": metadata})
                return result
        except Exception as e:
            # Fallback si Langfuse échoue
            print(f"⚠️ Langfuse non disponible: {e}")
            return self._route_logic(q, metadata)
    
    def _route_logic(self, q: str, metadata: dict) -> str:
        """Logique de routage principale (identique à votre version)"""
        
        # 1. Vérifier si la question contient un nom de client
        for name in self.client_names:
            if name in q:
                metadata["decision_steps"].append("client_name_match")
                metadata["matched_keywords"].append(name)
                return "DATA"
        
        # 2. Vérifier pattern "Je m'appelle [Prénom] [Nom]"
        if "je m'appelle" in q or "m'appelle" in q:
            metadata["decision_steps"].append("self_introduction")
            # Extraire le nom après "je m'appelle"
            parts = q.split("je m'appelle")
            if len(parts) > 1:
                potential_name = parts[1].strip().split()[0] if parts[1].strip() else ""
                if potential_name:
                    metadata["matched_keywords"].append(f"je_m_appelle_{potential_name}")
            return "DATA"
        
        # 3. Questions iPhone, prix, catalogue → PDF
        iphone_keywords = ["iphone", "téléphone", "smartphone", "appareil"]
        price_keywords = ["prix", "coûte", "combien", "€", "euro", "budget", "tarif"]
        catalog_keywords = ["catalogue", "modèle", "128gb", "256gb", "512gb", "1tb", "disponible"]
        
        all_pdf_keywords = iphone_keywords + price_keywords + catalog_keywords
        matched_keywords = [kw for kw in all_pdf_keywords if kw in q]
        
        if matched_keywords:
            metadata["decision_steps"].append("pdf_iphone_price_catalog")
            metadata["matched_keywords"].extend(matched_keywords)
            return "PDF"
        
        # 4. FAQs, procédures, comment faire → PDF
        procedure_keywords = [
            "comment", "activer", "configurer", "désactiver", "paramétrer",
            "pourquoi", "quels", "quelles", "quel", "quelle", "que faire",
            "procédure", "étape", "guide", "tutoriel", "faire", "résilier",
            "souscrire", "abonner", "changer", "modifier", "mettre à jour"
        ]
        
        matched_procedure = [kw for kw in procedure_keywords if kw in q]
        if matched_procedure:
            metadata["decision_steps"].append("pdf_procedure")
            metadata["matched_keywords"].extend(matched_procedure)
            return "PDF"
        
        # 5. Questions techniques, support → PDF
        tech_keywords = [
            "mms", "sms", "roaming", "internet", "data", "réseau",
            "forfait", "abonnement", "facture", "paiement", "mobile",
            "téléphonie", "support", "assistance", "aide", "service"
        ]
        
        matched_tech = [kw for kw in tech_keywords if kw in q]
        if matched_tech:
            metadata["decision_steps"].append("pdf_tech")
            metadata["matched_keywords"].extend(matched_tech)
            return "PDF"
        
        # 6. Statistiques, comptes, listes → DATA
        data_keywords = [
            "combien de", "nombre de", "total de", "quantité de",
            "statistique", "moyenne", "minimum", "maximum", "liste",
            "tous les", "chaque", "par", "groupé", "trié", "filtré","consommation" ,
            "client", "clients", "abonné", "abonnés", "utilisateur","historique","minutes"
        ]
        
        matched_data = [kw for kw in data_keywords if kw in q]
        if matched_data:
            metadata["decision_steps"].append("data_stats")
            metadata["matched_keywords"].extend(matched_data)
            return "DATA"
        
        # 7. Par défaut: WEB
        metadata["decision_steps"].append("default_web")
        return "WEB"