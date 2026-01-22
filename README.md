# 📡 TelecomPlus – Système Multi-Agents RAG  
**Dauphine Generative AI Project 2025 – 2026**  
Université Paris Dauphine – IASD  

---

## 🎯 Objectif du projet

Ce projet implémente un **système agentique multi-agents RAG** capable de répondre automatiquement à des questions clients dans le contexte d’un **opérateur télécom fictif (TelecomPlus)**.

Le système traite des questions liées à :

- 📱 Smartphones (catalogue, prix)
- 📦 Forfaits et abonnements
- 💳 Facturation et paiement
- 🌍 Roaming international
- 📊 Données clients (consommation, factures)

L’architecture repose sur :
- une **orchestration par agent routeur**
- des **agents spécialisés**
- une **observabilité complète via Langfuse**

---

## 🧠 Architecture du système agentique

Le système est composé de **4 agents principaux**, orchestrés par un Router Agent.

### 🔀 Router Agent
- Analyse la question utilisateur
- Sélectionne dynamiquement l’agent le plus pertinent
- Garantit une séparation claire des responsabilités

### 📄 PDF Agent (RAG)
S’appuie sur des documents internes (PDF : FAQ, catalogue téléphones)

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

Le projet intègre **Langfuse** afin d’assurer une **traçabilité complète des interactions LLM** au sein du système multi-agents.

### 🔍 Intégration Langfuse
- Client centralisé :  
  `src/monitoring/langfuse_client.py`
- Instrumentation intégrée dans :
  - `app.py`
  - les agents
  - le routeur

### 📊 Métriques collectées
Langfuse permet de tracer :

- ✅ Réponses LLM
- 🔗 Chaînes d’agents (routing et orchestration)
- 🛠️ Tool calls (PDF Agent, Data Agent, Web Agent)
- ⏱️ Latence par agent et par requête
- 🧠 Prompts et outputs

➡️ Ces métriques sont utilisées **uniquement pour le monitoring et l’observabilité**, et non pour l’évaluation.

---

## 🧪 Évaluation automatique (LLM as a Judge)

⚠️ **L’évaluation n’est pas implémentée dans `app.py`.**

### 📄 Fichier dédié
- `evaluate.py`

### 🧠 Méthodologie
- Utilisation d’un **LLM as a Judge**
- Chaque réponse est notée sur **3 points**
- Évaluation **hors ligne**, indépendante du monitoring Langfuse

### ✅ Résultats globaux
- **Score moyen** : 2.24 / 3  
- **Score total** : 56 / 75  

### 📊 Performance par agent

| Agent       | Score moyen |
|------------|-------------|
| PDF Agent  | 2.35 / 3 |
| Data Agent | 1.86 / 3 |
| Web Agent  | 3.00 / 3 |

### 📈 Distribution des scores
- 3 / 3 : 48 %
- 2 / 3 : 32 %
- ≤ 1 / 3 : 20 %

Les erreurs restantes correspondent principalement à des **informations absentes des sources**, choix volontaire afin d’éviter toute hallucination.

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



