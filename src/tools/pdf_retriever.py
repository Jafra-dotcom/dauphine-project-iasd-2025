from pathlib import Path
import re
import logging

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

# Configuration du logging
logging.getLogger("pypdf").setLevel(logging.ERROR)


class PDFRetriever:
    def __init__(self, pdf_dir: str, embedding_model: str):
        self.pdf_dir = Path(pdf_dir)
        self.embeddings = OllamaEmbeddings(model=embedding_model)
        self.vectorstore = None
        
        # ===============================
        # 📊 TABLEAU STRUCTURÉ DES PRIX
        # ===============================
        self.iphone_prices = {
            "iPhone X":  {"256GB": 749},
            "iPhone 11": {"128GB": 559, "256GB": 659},
            "iPhone 12": {"128GB": 729, "256GB": 829},
            "iPhone 13": {"128GB": 809, "256GB": 929, "512GB": 1159},
            "iPhone 14": {"128GB": 869, "256GB": 999, "512GB": 1259},
            "iPhone 15": {"128GB": 969, "256GB": 1099, "512GB": 1359},
            "iPhone 16": {"128GB": 1019, "256GB": 1149, "512GB": 1409},
            "iPhone 17": {"256GB": 1299, "512GB": 1449, "1TB": 1799},
        }

        # ===============================
        # 📌 FAITS SIMPLES
        # ===============================
        self.iphone_facts = {
            "iPhone 13": {"year": 2021, "camera": 12},
            "iPhone 14": {"year": 2022, "camera": 12},
            "iPhone 15": {"year": 2023, "camera": 48},
            "iPhone 16": {"year": 2024, "camera": 48},
        }

    # ------------------------------------------------------------------
    # 📄 CHARGEMENT DES PDFS (ROBUSTE)
    # ------------------------------------------------------------------

    def load_documents(self):
        documents = []
        valid_pdfs = []
        
        # Lister tous les fichiers PDF
        pdf_files = list(self.pdf_dir.glob("*.pdf"))
        
        if not pdf_files:
            print("⚠️ Aucun fichier PDF trouvé dans le dossier.")
            return documents
            
        print(f"📁 Trouvé {len(pdf_files)} fichier(s) PDF")
        
        for pdf_file in pdf_files:
            try:
                print(f"📄 Chargement de : {pdf_file.name}")
                
                # Tenter de lire le PDF avec plusieurs essais
                max_retries = 2
                for attempt in range(max_retries):
                    try:
                        loader = PyPDFLoader(str(pdf_file))
                        doc = loader.load()
                        
                        if doc:
                            documents.extend(doc)
                            valid_pdfs.append(pdf_file.name)
                            print(f"✅ PDF chargé avec succès : {pdf_file.name}")
                            break
                        else:
                            print(f"⚠️ PDF vide : {pdf_file.name}")
                            
                    except Exception as e:
                        if attempt < max_retries - 1:
                            print(f"⚠️ Nouvelle tentative pour {pdf_file.name}...")
                            continue
                        else:
                            raise e
                            
            except Exception as e:
                print(f"❌ Erreur avec {pdf_file.name} : {str(e)}")
                
        print(f"✅ {len(valid_pdfs)}/{len(pdf_files)} PDF(s) chargé(s) avec succès")
        return documents

    # ------------------------------------------------------------------
    # 🧠 INDEXATION VECTORIELLE
    # ------------------------------------------------------------------

    def build_index(self):
        documents = self.load_documents()
        
        if not documents:
            print("⚠️ Aucun document à indexer.")
            return
            
        print(f"📊 Indexation de {len(documents)} document(s)...")
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            separators=[
                "\n\nQ", "\nQ",
                "\n\nR", "\nR",
                "\n\n",
                "\n",
                ".",
                " ",
                ""
            ]
        )

        splits = splitter.split_documents(documents)
        print(f"🔪 Découpé en {len(splits)} morceau(x)")
        
        if splits:
            self.vectorstore = FAISS.from_documents(splits, self.embeddings)
            print("✅ Index vectoriel construit avec succès")
        else:
            print("⚠️ Aucun morceau à indexer.")

    # ------------------------------------------------------------------
    # 🔍 ROUTAGE INTELLIGENT
    # ------------------------------------------------------------------

    def retrieve(self, question: str) -> str:
        q = question.lower()

        # 🔥 PRIORITÉ ABSOLUE : PRIX / BUDGET
        if any(k in q for k in ["prix", "€", "budget", "cher", "cout", "coût"]):
            result = self._price_context(question)
            if result:
                return result

        # 📆 ANNÉE DE SORTIE
        if any(k in q for k in ["commercialisé", "sorti", "année", "date"]):
            result = self._year_context(question)
            if result:
                return result

        # 📷 CAMÉRA
        if any(k in q for k in ["mpx", "méga", "mégapixel", "caméra", "photo"]):
            result = self._camera_context(question)
            if result:
                return result

        # 📄 FALLBACK VECTORIEL (FAQ, CGU, etc.)
        try:
            if not self.vectorstore:
                self.build_index()
            
            if self.vectorstore:
                docs = self.vectorstore.similarity_search(question, k=4)
                if docs:
                    return "\n".join(d.page_content for d in docs)
        except Exception as e:
            print(f"⚠️ Erreur lors de la recherche vectorielle : {e}")

        # Fallback par défaut
        return "Aucune information pertinente trouvée dans les documents."

    # ------------------------------------------------------------------
    # 🔧 MÉTHODES SPÉCIALISÉES
    # ------------------------------------------------------------------

    def _price_context(self, question: str) -> str:
        q = question.lower()

        # 🎯 PRIX EXACT
        for model, capacities in self.iphone_prices.items():
            if model.lower() in q:
                for cap, price in capacities.items():
                    if cap.lower() in q:
                        return f"{model} – {cap} : {price}€\n(Source : Catalogue téléphones)"

        # 💰 BUDGET
        budget_match = re.search(r'(\d{3,4})\s*€?', q)
        if budget_match:
            budget = int(budget_match.group(1))
            options = []

            for model, caps in self.iphone_prices.items():
                for cap, price in caps.items():
                    if price <= budget:
                        options.append(f"{model} – {cap} : {price}€")

            if options:
                return "IPHONES DANS VOTRE BUDGET :\n" + "\n".join(sorted(options))

        # 🏷️ MOINS CHER
        if "moins cher" in q:
            cheapest = None
            for model, caps in self.iphone_prices.items():
                for cap, price in caps.items():
                    if cheapest is None or price < cheapest[2]:
                        cheapest = (model, cap, price)

            if cheapest:
                return (
                    f"L'iPhone le moins cher disponible est : "
                    f"{cheapest[0]} – {cheapest[1]} : {cheapest[2]}€"
                )

        return ""

    def _year_context(self, question: str) -> str:
        match = re.search(r'(20\d{2})', question)
        if not match:
            return ""

        year = int(match.group(1))
        models = [
            m for m, f in self.iphone_facts.items()
            if f["year"] == year
        ]

        if models:
            return f"iPhone commercialisés en {year} : " + ", ".join(models)

        return ""

    def _camera_context(self, question: str) -> str:
        match = re.search(r'(\d+)\s*mpx', question.lower())
        if not match:
            return ""

        mpx = int(match.group(1))
        models = [
            m for m, f in self.iphone_facts.items()
            if f["camera"] >= mpx
        ]

        if models:
            return f"iPhone avec au moins {mpx} Mpx : " + ", ".join(models)

        return ""