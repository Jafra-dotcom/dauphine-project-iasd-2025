# 📡 TelecomPlus – Système Multi-Agents RAG  
**Dauphine Generative AI Project 2025 – 2026**  
Université Paris Dauphine – IASD  

---

## 🎯 Objectif du projet

Ce projet implémente un **système agentique multi-agents basé sur RAG (Retrieval-Augmented Generation)** capable de répondre automatiquement à des questions clients dans le contexte d’un **opérateur télécom fictif (TelecomPlus)**.

Le système traite des questions liées à :

- 📱 Smartphones (catalogue, prix)
- 📦 Forfaits et abonnements
- 💳 Facturation et paiement
- 🌍 Roaming international
- 📊 Données clients (consommation, factures)

L’architecture repose sur :
- une **orchestration intelligente via un Router Agent**
- des **agents spécialisés**
- une **observabilité complète grâce à Langfuse**
- une **évaluation indépendante via LLM as a Judge**

---

## 🧠 Architecture du système agentique

Le système est composé de **4 agents principaux**, orchestrés par un **Router Agent**.

### 🔀 Router Agent
- Analyse la question utilisateur
- Sélectionne dynamiquement l’agent le plus pertinent
- Garantit une séparation claire des responsabilités

### 📄 PDF Agent (RAG)
S’appuie sur des documents internes (PDF : FAQ, catalogue téléphones)

**Pipeline RAG :**
1. Chargement des PDFs  
2. Découpage sémantique (chunking)  
3. Indexation vectorielle avec FAISS  
4. Recherche des passages pertinents  
5. Génération de la réponse via LLM  

### 📊 Data Agent
- Accède à des données structurées (CSV / tables)
- Répond à des questions personnalisées :
  - consommation
  - factures
  - roaming

### 🌐 Web Agent
- Gère les questions générales hors périmètre interne
- Fournit des réponses factuelles à portée générale

---

## 📈 Observabilité & Monitoring (Langfuse)

Le projet intègre **Langfuse** afin d’assurer une **traçabilité complète des interactions LLM** dans le système multi-agents.

### 🔍 Intégration Langfuse
- Client centralisé : `src/monitoring/langfuse_client.py`
- Instrumentation intégrée dans :
  - `app.py`
  - les agents
  - le routeur

### 📊 Métriques collectées
Langfuse permet de tracer :

- ✅ Réponses LLM
- 🔗 Chaînes d’agents (routing et orchestration)
- 🛠️ Tool calls (PDF, Data, Web Agents)
- ⏱️ Latence par agent et par requête
- 🧠 Prompts et outputs

➡️ Ces métriques sont utilisées **exclusivement pour le monitoring** et **pas pour l’évaluation**.

---

## 🧪 Évaluation automatique (LLM as a Judge)

⚠️ **L’évaluation n’est pas implémentée dans `app.py`.**

### 📄 Fichier dédié
- `evaluate.py`

### 🧠 Méthodologie
- Utilisation d’un **LLM as a Judge**
- Chaque réponse est notée sur **3 points**
- Évaluation **hors ligne**, indépendante du monitoring Langfuse

### 📊 Résultats finaux

**🎯 Score moyen : 2.24 / 3**  
**🏆 Score total : 56 / 75**

#### 📊 Distribution des scores
- 0 / 3 : 1 question (4 %)
- 1 / 3 : 3 questions (12 %)
- 2 / 3 : 10 questions (40 %)
- 3 / 3 : 11 questions (44 %)

#### 📈 Performance par agent
- **PDF Agent** : 2.53 / 3 (17 questions)
- **WEB Agent** : 2.00 / 3 (1 question)
- **DATA Agent** : 1.57 / 3 (7 questions)

Les écarts proviennent principalement d’informations absentes des sources, choix volontaire afin **d’éviter toute hallucination**.

---

## 🛠️ Choix techniques

### 🔮 Modèles
- **LLM** : `mistral-opt` (via Ollama)
- **Embeddings** : `nomic-embed-text`

### 📐 Vectorisation
- **FAISS** – rapide, léger, local

### 🧩 Framework
- **LangChain** – structuration agentique claire

---

## 📂 Structure du projet

dauphine-project-iasd-2025/
├── app.py
├── evaluate.py
├── README.md
├── requirements.txt
├── llm_evaluation.csv
├── mistral-optimized.txt
├── data/
│   ├── pdfs/
│   ├── xlsx/
│   └── vectorstore/
├── src/
│   ├── agents/
│   │   ├── pdf_agent.py
│   │   ├── data_agent.py
│   │   ├── web_agent.py
│   │   └── router.py
│   ├── monitoring/
│   │   └── langfuse_client.py
│   ├── tools/
│   │   ├── pdf_retriever.py
│   │   └── data_tools.py
│   └── config.py

## ▶️ Installation

1️⃣ Cloner le projet  
git clone <repo_url>  
cd dauphine-project-iasd-2025  

2️⃣ Créer l'environnement virtuel  
python -m venv venv  
source venv/bin/activate   # Linux / Mac  
venv\Scripts\activate      # Windows  

3️⃣ Installer les dépendances  
pip install -r requirements.txt  

4️⃣ Lancer Ollama  
ollama run mistral-opt  

---

## ▶️ Exécution

Lancer l'application (monitoring Langfuse actif)  
streamlit run app.py  

Lancer l'évaluation automatique (LLM as a Judge)  
python evaluate.py  

---

## ⚠️ Limites & améliorations possibles

- Enrichissement des métadonnées produit  
- Amélioration des règles métier du Data Agent  
- Routage hybride (règles + score sémantique)  
- Exploitation avancée du dashboard Langfuse (alerting, analyse de latence)  

---

## 🏁 Conclusion

Ce projet démontre une implémentation complète, observable et évaluée d'un système multi-agents RAG, combinant :

- orchestration intelligente  
- fiabilité des réponses  
- monitoring LLM avancé via Langfuse  
- évaluation automatique indépendante (LLM as a Judge)
```




