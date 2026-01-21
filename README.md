# Dauphine Generative AI Project 2025 - 2026
**Université Paris Dauphine - IASD 2025-2026**
# 📡 TelecomPlus – Système Multi-Agents RAG

## 🎯 Objectif du projet

Ce projet implémente un **système agentique multi-agents** capable de répondre automatiquement à des questions clients dans le contexte d’un opérateur télécom fictif (*TelecomPlus*).

Le système traite des questions liées :

* aux **smartphones** (catalogue, prix)
* aux **forfaits et abonnements**
* à la **facturation et au paiement**
* au **roaming international**
* aux **données clients** (consommation, factures)

Il repose sur une architecture **RAG (Retrieval-Augmented Generation)** combinée à un **router d’agents spécialisés**.

---

## 🧠 Architecture du système agentique

Le système est composé de **4 agents principaux**, orchestrés par un agent routeur :

### 🔀 Router Agent

* Analyse la question utilisateur
* Sélectionne automatiquement l’agent le plus pertinent
* Garantit une séparation claire des responsabilités

### 📄 PDF Agent (RAG)

* S’appuie sur des **documents PDF internes** (FAQ, catalogue téléphones)
* Pipeline :

  1. Chargement des PDFs
  2. Découpage sémantique (chunks)
  3. Indexation vectorielle FAISS
  4. Recherche des passages pertinents
  5. Génération de réponse via LLM

### 📊 Data Agent

* Accède à des **données structurées clients** (CSV / tables)
* Répond à des questions personnalisées :

  * consommation
  * factures
  * roaming

### 🌐 Web Agent

* Gère les questions générales non couvertes par les données internes
* Fournit des réponses factuelles à portée générale

---

## 🛠️ Choix techniques et justifications

### Modèles

* **LLM** : `mistral-opt` (via Ollama)

  * Modèle local
  * Bon compromis performance / coût
  * Pas de dépendance cloud

* **Embeddings** : `nomic-embed-text`

  * Adapté à la recherche sémantique
  * Performant pour des documents courts à moyens

### Vectorisation

* **FAISS**

  * Rapide
  * Léger
  * Idéal pour un projet local

### Framework

* **LangChain**

  * Facilite la structuration agentique
  * Chaînes RAG explicites et modulaires

### Philosophie de conception

* ❌ Pas d’hallucination
* ✅ Réponses uniquement basées sur les sources
* ✅ Préférence donnée à la fiabilité plutôt qu’à l’exhaustivité

---

## 📂 Structure du projet

```
.
├── app.py
├── evaluate.py
├── README.md
├── requirements.txt
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
│   ├── tools/
│   │   ├── pdf_retriever.py
│   │   └── data_tools.py
│   └── config.py
└── llm_evaluation.csv
```

---

## ▶️ Installation

### 1️⃣ Cloner le projet

```bash
git clone <repo_url>
cd telecomplus-rag
```

### 2️⃣ Créer l’environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4️⃣ Lancer Ollama

```bash
ollama run mistral-opt
```

---

## ▶️ Exécution

### Lancer l’application

```bash
streamlit run app.py
```

### Lancer l’évaluation automatique

```bash
python evaluate.py
```

---

## 📊 Résultats d’évaluation

L’évaluation est réalisée via un **LLM Judge**, notant chaque réponse sur **3 points**.

### Résultats globaux

* **Score moyen** : **2.24 / 3**
* **Score total** : **56 / 75**

### Performance par agent

| Agent      | Score moyen  |
| ---------- | ------------ |
| PDF Agent  | **2.35 / 3** |
| Data Agent | 1.86 / 3     |
| Web Agent  | 3.00 / 3     |

### Distribution des scores

* 3/3 : 48%
* 2/3 : 32%
* 1/3 ou moins : 20%

Les erreurs restantes correspondent principalement à des **informations absentes des sources**, choix volontaire afin d’éviter toute hallucination.

---

## ⚠️ Limites et améliorations possibles

* Ajout de métadonnées produit (année de sortie, caméra, autonomie)
* Enrichissement des règles métier du Data Agent
* Amélioration du routage hybride (règles + score sémantique)

---

## 🏁 Conclusion

Ce projet démontre la mise en œuvre complète d’un **système agentique RAG**, robuste, explicable et évalué automatiquement, adapté à des cas d’usage réalistes en entreprise.

