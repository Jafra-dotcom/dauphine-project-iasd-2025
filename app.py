import streamlit as st
from langchain_ollama import OllamaLLM
from src.agents.data_agent import DataAgent
from src.agents.web_agent import WebAgent
from src.agents.router import RouterAgent
from src.agents.pdf_agent import PDFAgent
st.set_page_config(page_title="Telecom Support", page_icon="📱")
st.title("📱 Assistant Client")

# LLM Judge avec les critères exacts
class LLMJudge:
    def __init__(self):
        try:
            self.llm = OllamaLLM(model="mistral-opt", temperature=0.0)
            self.available = True
        except:
            self.available = False
    
    def score(self, question, response):
        if not self.available:
            return None
        
        prompt = f"""Évalue cette réponse sur une échelle de 0 à 3.

CRITÈRES:
3 = La réponse est complète et précise
2 = La réponse est globalement correcte mais manque des détails  
1 = La réponse est partiellement pertinente mais incomplète ou imprécise
0 = La réponse est fausse, hors sujet ou "je ne sais pas"

QUESTION: {question}

RÉPONSE: {response}

Réponds SEULEMENT avec un chiffre: 0, 1, 2 ou 3"""
        
        try:
            llm_response = str(self.llm.invoke(prompt)).strip()
            
            for char in llm_response:
                if char in '0123':
                    return int(char)
            
            if any(word in llm_response.lower() for word in ['excellent', 'parfait', 'complet', '3']):
                return 3
            elif any(word in llm_response.lower() for word in ['correct', 'bon', '2']):
                return 2
            elif any(word in llm_response.lower() for word in ['partiel', 'imprécis', '1']):
                return 1
            else:
                return 0
                
        except:
            return None

# Initialiser les agents
@st.cache_resource
def get_agents():
    return {
        "pdf": PDFAgent(),
        "data": DataAgent(),
        "web": WebAgent(),
        "router": RouterAgent(),
        "judge": LLMJudge()
    }

# Fonction de réponse
def get_answer(question):
    agents = get_agents()
    route = agents["router"].route(question)
    
    if route == "PDF":
        response = agents["pdf"].run(question)
    elif route == "DATA":
        response = agents["data"].run(question)
    else:
        response = agents["web"].run(question)
    
    # Évaluer la réponse
    score = agents["judge"].score(question, response)
    
    return response, score, route

# Historique
if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher historique
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant" and msg["score"] is not None:
            score_emoji = ["🔴", "🟠", "🟡", "🟢"][msg["score"]]
            st.caption(f"{score_emoji} Score: {msg['score']}/3")

# Input utilisateur
if question := st.chat_input("Posez votre question..."):
    # Message utilisateur
    st.session_state.messages.append({"role": "user", "content": question})
    st.chat_message("user").write(question)
    
    # Obtenir réponse
    response, score, route = get_answer(question)
    
    # Message assistant
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response,
        "score": score
    })
    
    with st.chat_message("assistant"):
        st.write(response)
        if score is not None:
            score_emoji = ["🔴", "🟠", "🟡", "🟢"][score]
            st.caption(f"{score_emoji} Score: {score}/3")
        else:
            st.caption("⚠️ Score non disponible")

# Sidebar
with st.sidebar:
    if st.button("Effacer l'historique"):
        st.session_state.messages = []
        st.rerun()
    
    st.write("**Critères :**")
    st.write("3 = Parfaitement exacte")
    st.write("2 = Globalement correcte")
    st.write("1 = Partiellement pertinente")
    st.write("0 = Fausse ou hors sujet")