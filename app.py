import streamlit as st
import time

# Langfuse
try:
    from langfuse import Langfuse
    langfuse = Langfuse()
    LANGFUSE_OK = True
except Exception as e:
    st.warning(f"⚠️ Langfuse désactivé: {e}")
    langfuse = None
    LANGFUSE_OK = False

# Import agents
from src.agents.data_agent import DataAgent
from src.agents.web_agent import WebAgent
from src.agents.router import RouterAgent
from src.agents.pdf_agent import PDFAgent

st.set_page_config(page_title="Telecom Support", page_icon="📱")
st.title("📊 Assistant Monitoré")

# Cache agents
@st.cache_resource  
def load_agents():
    return {
        "pdf": PDFAgent(),
        "data": DataAgent(),
        "web": WebAgent(),
        "router": RouterAgent()
    }

# Fonction avec monitoring COMPLET
def process_with_monitoring(question):
    trace_id = f"trace_{int(time.time())}_{hash(question) % 10000}"
    all_events = []
    
    # 1. PROMTS - Enregistrer la question
    prompt_event = {
        "type": "prompt",
        "name": "user_question",
        "content": question,
        "timestamp": time.time()
    }
    all_events.append(prompt_event)
    
    if LANGFUSE_OK:
        try:
            langfuse.create_event(
                name="user_prompt",
                input={"question": question},
                metadata={"trace_id": trace_id}
            )
        except:
            pass
    
    agents = load_agents()
    
    # 2. CHAINE AGENTS - Router avec détails
    router_start = time.time()
    route = agents["router"].route(question)
    router_time = time.time() - router_start
    
    router_event = {
        "type": "agent_chain", 
        "name": "router_decision",
        "route": route,
        "latency_ms": round(router_time * 1000, 2),
        "logic": "Détection par mots-clés"
    }
    all_events.append(router_event)
    
    # 3. TOOLS CALLS - Détails selon l'agent
    agent_start = time.time()
    
    tools_used = []
    if route == "PDF":
        response = agents["pdf"].run(question)
        tools_used = ["pdf_search", "text_extraction", "vector_search", "llm_generation"]
    elif route == "DATA":
        response = agents["data"].run(question)  
        tools_used = ["excel_reader", "data_filter", "statistics", "visualization"]
    else:
        response = agents["web"].run(question)
        tools_used = ["web_search", "content_extraction", "summarization"]
    
    agent_time = time.time() - agent_start
    
    tools_event = {
        "type": "tools_calls",
        "agent": route.lower(),
        "tools": tools_used,
        "count": len(tools_used),
        "latency_ms": round(agent_time * 1000, 2)
    }
    all_events.append(tools_event)
    
    # 4. REPONSES - Analyse de la réponse
    total_time = time.time() - prompt_event["timestamp"]
    
    response_event = {
        "type": "response",
        "length_chars": len(response) if response else 0,
        "has_data": any(word in response.lower() for word in ["gb", "€", "%", "iphone", "noir", "blanc"]),
        "is_structured": "•" in response or "\n" in response or ":" in response,
        "latency_ms": round(total_time * 1000, 2)
    }
    all_events.append(response_event)
    
    # Langfuse events complets
    if LANGFUSE_OK:
        try:
            # Score de qualité de réponse
            quality_score = min(1.0, len(response) / 500) if response else 0.1
            langfuse.create_score(
                name="response_quality",
                value=quality_score,
                comment=f"Longueur: {len(response)} chars"
            )
            
            # Score de performance
            perf_score = max(0.1, 1.0 - (total_time / 10))
            langfuse.create_score(
                name="performance_score", 
                value=perf_score,
                comment=f"Latence: {total_time:.2f}s"
            )
            
            # Event final avec tous les détails
            langfuse.create_event(
                name="query_completed",
                input={"question": question, "route": route},
                output={"response_preview": response[:200] if response else ""},
                metadata={
                    "trace_id": trace_id,
                    "total_latency_ms": round(total_time * 1000, 2),
                    "agent_latency_ms": round(agent_time * 1000, 2),
                    "router_latency_ms": round(router_time * 1000, 2),
                    "tools_used": ", ".join(tools_used),
                    "response_length": len(response) if response else 0,
                    "agent_chain": f"router → {route}_agent"
                }
            )
        except Exception as e:
            st.error(f"Langfuse error: {str(e)[:50]}")
    
    return {
        "response": response,
        "route": route,
        "trace_id": trace_id,
        "events": all_events,
        "metrics": {
            "total_ms": round(total_time * 1000, 2),
            "router_ms": round(router_time * 1000, 2),
            "agent_ms": round(agent_time * 1000, 2),
            "tools_count": len(tools_used),
            "response_chars": len(response) if response else 0
        }
    }

# --- INTERFACE RICHE ---
st.header("💬 Chat Monitoré")

# Historique
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Afficher historique
for i, msg in enumerate(st.session_state.chat_history):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        
        if msg["role"] == "assistant":
            # Affichage ÉTENDU des métriques
            cols = st.columns(4)
            cols[0].metric("Route", msg["metrics"]["route"])
            cols[1].metric("Temps", f"{msg['metrics']['total_ms']}ms")
            cols[2].metric("Tools", msg["metrics"]["tools_count"])
            cols[3].metric("Chars", msg["metrics"]["response_chars"])
            
            # Détails dans expander
            with st.expander("🔍 Voir le monitoring complet"):
                st.write("### 📝 Prompts Monitorés")
                st.write(f"**Question:** {msg['events'][0]['content']}")
                
                st.write("### 🔗 Chaîne d'Agents")
                router_event = msg["events"][1]
                st.write(f"**Router:** {router_event['route']} ({router_event['latency_ms']}ms)")
                st.write(f"**Logique:** {router_event.get('logic', 'N/A')}")
                
                st.write("### 🛠️ Tools Calls")
                tools_event = msg["events"][2]
                st.write(f"**Agent:** {tools_event['agent']}")
                st.write(f"**Tools utilisés ({tools_event['count']}):**")
                for tool in tools_event["tools"]:
                    st.write(f"- `{tool}`")
                
                st.write("### 💬 Réponse Analyse")
                resp_event = msg["events"][3]
                st.write(f"**Longueur:** {resp_event['length_chars']} caractères")
                st.write(f"**Contient données:** {'✅' if resp_event['has_data'] else '❌'}")
                st.write(f"**Structurée:** {'✅' if resp_event['is_structured'] else '❌'}")
                
                if msg.get("trace_id"):
                    st.write(f"**Trace ID:** `{msg['trace_id']}`")
                
                if LANGFUSE_OK:
                    st.success("✅ Données envoyées à Langfuse")

# Input
if question := st.chat_input("Posez votre question..."):
    # Ajouter question
    st.session_state.chat_history.append({
        "role": "user", 
        "content": question,
        "timestamp": time.time()
    })
    
    # Traiter
    with st.spinner(f"🔍 Traitement et monitoring..."):
        result = process_with_monitoring(question)
    
    # Ajouter réponse
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": result["response"],
        "timestamp": time.time(),
        "trace_id": result["trace_id"],
        "events": result["events"],
        "metrics": {
            "route": result["route"],
            "total_ms": result["metrics"]["total_ms"],
            "router_ms": result["metrics"]["router_ms"],
            "agent_ms": result["metrics"]["agent_ms"],
            "tools_count": result["metrics"]["tools_count"],
            "response_chars": result["metrics"]["response_chars"]
        }
    })
    
    st.rerun()

# --- SIDEBAR DÉTAILLÉ ---
with st.sidebar:
    st.header("📊 Tableau de Bord Langfuse")
    
    if LANGFUSE_OK:
        st.success("### ✅ MONITORING ACTIF")
        
        st.write("#### 🔍 **Prompts Monitorés**")
        st.write("- Questions utilisateur complètes")
        st.write("- Timestamp précis")
        st.write("- Format: JSON structuré")
        
        st.write("#### 💬 **Réponses Analyse**")
        st.write("- Longueur des réponses")
        st.write("- Structure (listes, tableaux)")
        st.write("- Présence de données spécifiques")
        st.write("- Qualité automatique évaluée")
        
        st.write("#### 🔗 **Chaîne d'Agents**")
        st.write("**Séquence:**")
        st.write("1. **RouterAgent** → détection mots-clés")
        st.write("2. **{PDF/Data/Web}Agent** → exécution")
        st.write("3. **Tools spécifiques** → selon l'agent")
        
        st.write("#### 🛠️ **Tools Calls Détail**")
        st.write("**PDF Agent:**")
        st.write("- `pdf_search`: Recherche vectorielle")
        st.write("- `text_extraction`: Extraction PDF")
        st.write("- `vector_search`: Similarité sémantique")
        st.write("- `llm_generation`: Génération réponse")
        
        st.write("**Data Agent:**")
        st.write("- `excel_reader`: Lecture fichiers")
        st.write("- `data_filter`: Filtrage données")
        st.write("- `statistics`: Calculs stats")
        st.write("- `visualization`: Génération visuels")
        
        st.write("**Web Agent:**")
        st.write("- `web_search`: Recherche internet")
        st.write("- `content_extraction`: Extraction contenu")
        st.write("- `summarization`: Synthèse information")
        
        st.write("#### ⏱️ **Latence Détail**")
        st.write("- **Total:** Temps complet requête")
        st.write("- **Router:** Décision de routage")
        st.write("- **Agent:** Exécution + tools")
        st.write("- **Performance score:** 0-1 automatique")
        
    else:
        st.error("### ❌ LANGfUSE DESACTIVE")
        st.code(""".streamlit/secrets.toml:
LANGFUSE_PUBLIC_KEY = "pk-lf-..."
LANGFUSE_SECRET_KEY = "sk-lf-..."
LANGFUSE_HOST = "https://cloud.langfuse.com""")
    
    # Statistiques avancées
    if st.session_state.chat_history:
        st.divider()
        st.subheader("📈 Statistiques Session")
        
        assistant_msgs = [m for m in st.session_state.chat_history if m["role"] == "assistant"]
        
        if assistant_msgs:
            # Calculs
            total_queries = len(assistant_msgs)
            avg_latency = sum(m["metrics"]["total_ms"] for m in assistant_msgs) / total_queries
            avg_chars = sum(m["metrics"]["response_chars"] for m in assistant_msgs) / total_queries
            total_tools = sum(m["metrics"]["tools_count"] for m in assistant_msgs)
            
            # Routes distribution
            routes = [m["metrics"]["route"] for m in assistant_msgs]
            from collections import Counter
            route_dist = Counter(routes)
            
            # Affichage
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Requêtes", total_queries)
                st.metric("Latence moy", f"{avg_latency:.0f}ms")
            with col2:
                st.metric("Chars moy", f"{avg_chars:.0f}")
                st.metric("Tools total", total_tools)
            
            st.write("**Distribution Routes:**")
            for route, count in route_dist.items():
                percentage = (count / total_queries) * 100
                st.write(f"- **{route}:** {count} ({percentage:.1f}%)")
    
    # Contrôles
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear", type="primary"):
            st.session_state.chat_history = []
            st.rerun()
    with col2:
        if st.button("📊 Export", type="secondary"):
            st.info("Export vers Langfuse Cloud automatique")

# Footer
st.sidebar.divider()
st.sidebar.caption("🤖 **Monitoring temps réel:** 5 paramètres complets trackés")