# 📡 TelecomPlus – Système Multi-Agents RAG  
**Dauphine Generative AI Project 2025 – 2026**  
Université Paris Dauphine – IASD  

---

## 🎯 Objectif du projet

Ce projet implémente un **système agentique multi-agents RAG** capable de répondre automatiquement à des questions clients dans le contexte d'un **opérateur télécom fictif (TelecomPlus)**.

Le système traite des questions liées à :

- 📱 Smartphones (catalogue, prix)
- 📦 Forfaits et abonnements
- 💳 Facturation et paiement
- 🌍 Roaming international
- 📊 Données clients (consommation, factures)

L'architecture repose sur :
- une **orchestration par agent routeur**
- des **agents spécialisés**
- une **observabilité complète via Langfuse**

---

## 🧠 Architecture du système agentique

Le système est composé de **4 agents principaux**, orchestrés par un Router Agent.

### 🔀 Router Agent
- Analyse la question utilisateur
- Sélectionne dynamiquement l'agent le plus pertinent
- Garantit une séparation claire des responsabilités

### 📄 PDF Agent (RAG)
S'appuie sur des documents internes (PDF : FAQ, catalogue téléphones)

**Pipeline RAG :**
1. Chargement des PDFs  
2. Découpage sémantique (chunking)  
3. Indexation vectorielle (FAISS)  
4. Recherche des passages pertinents  
5. Génération de réponse via LLM  

### 📊 Data Agent
- Accède à des données structurées (CSV / tables)
- Répond à des questions personnalisées :
  - consommation
  - factures
  - roaming

### 🌐 Web Agent
- Gère les questions générales
- Fournit des réponses factuelles hors périmètre interne

---

## 📈 Observabilité & Monitoring (Langfuse)

Le projet intègre **Langfuse** afin d'assurer une **traçabilité complète des interactions LLM** au sein du système multi-agents.

### 🔍 Intégration Langfuse
- Client centralisé : `src/monitoring/langfuse_client.py`
- Instrumentation intégrée dans :
  - `app.py`
  - les agents
  - le routeur

### 📊 Métriques collectées
Langfuse permet de tracer :

- ✅ Réponses LLM
- 🔗 Chaînes d'agents (routing et orchestration)
- 🛠️ Tool calls (PDF Agent, Data Agent, Web Agent)
- ⏱️ Latence par agent et par requête
- 🧠 Prompts et outputs

➡️ Ces métriques sont utilisées **uniquement pour le monitoring**, et **pas pour l'évaluation**.

---

## 🧪 Évaluation automatique (LLM as a Judge)

⚠️ **L'évaluation n'est pas implémentée dans `app.py`.**

### 📄 Fichier dédié
- `evaluate.py`

### 🧠 Méthodologie
- Utilisation d'un **LLM as a Judge**
- Chaque réponse est notée sur **3 points**
- Évaluation **hors ligne**, indépendante du monitoring Langfuse

### 📊 RÉSULTATS FINAUX
================================================================================
🎯 Score moyen: 2.32/3  
🏆 Score total: 58/75  

### 📊 Distribution des scores:
- 0/3: 1 questions (4.0%)
- 1/3: 4 questions (16.0%) ███
- 2/3: 6 questions (24.0%) ████
- 3/3: 14 questions (56.0%) ███████████

### 📈 Performance par agent:
- **PDF Agent**: 2.47/3 (17 questions)
- **WEB Agent**: 3.00/3 (1 questions)  
- **DATA Agent**: 1.86/3 (7 questions)


Les erreurs restantes correspondent principalement à des **informations absentes des sources**, choix volontaire afin d'éviter toute hallucination.

---

## 🛠️ Choix techniques

### 🔮 Modèles
- **LLM** : `mistral-opt` (via Ollama)
  - Modèle local
  - Bon compromis performance / coût
  - Aucune dépendance cloud
- **Embeddings** : `nomic-embed-text`

### 📐 Vectorisation
- **FAISS**
  - Rapide
  - Léger
  - Adapté aux projets locaux

### 🧩 Framework
- **LangChain**
  - Structuration agentique claire
  - Chaînes RAG modulaires

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
---

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

## 🎯 Après ces modifications, votre dépôt sera parfait !



