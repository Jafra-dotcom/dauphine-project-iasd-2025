import pandas as pd
from langchain_community.llms import Ollama
from src.agents.pdf_agent import PDFAgent
from src.agents.data_agent import DataAgent
from src.agents.web_agent import WebAgent
from src.agents.router import RouterAgent

class LLMJudge:
    def __init__(self):
        self.llm = Ollama(model="mistral-opt", temperature=0.0)
    
    def score(self, question, expected, actual):
        prompt = f"""Évalue cette réponse sur une échelle de 0 à 3.

CRITÈRES:
3 = La réponse correspond parfaitement à l'attendu, est complète et précise
2 = La réponse est globalement correcte mais manque des détails  
1 = La réponse est partiellement pertinente mais incomplète ou imprécise
0 = La réponse est fausse, hors sujet ou "je ne sais pas"

QUESTION: {question}

RÉPONSE ATTENDUE: {expected}

RÉPONSE DONNÉE: {actual}

Réponds SEULEMENT avec un chiffre: 0, 1, 2 ou 3"""
        
        # Appel direct au LLM
        response = str(self.llm.invoke(prompt)).strip()
        
        # Prendre le premier chiffre de la réponse
        for char in response:
            if char in '0123':
                return int(char)
        
        # Si aucun chiffre valide trouvé, analyser le contenu
        if any(word in response.lower() for word in ['excellent', 'parfait', 'complet', '3']):
            return 3
        elif any(word in response.lower() for word in ['correct', 'bon', '2']):
            return 2
        elif any(word in response.lower() for word in ['partiel', 'imprécis', '1']):
            return 1
        else:
            return 0

def evaluate():
    print("🚀 Évaluation avec LLM Judge...")
    
    # Initialiser les agents
    agents = {
        "PDF": PDFAgent(),
        "DATA": DataAgent(),
        "WEB": WebAgent()
    }
    router = RouterAgent()
    judge = LLMJudge()
    
    # Charger les questions
    df = pd.read_excel("data/evaluation_questions.xlsx")
    results = []
    
    print(f"📋 Évaluation de {len(df)} questions...")
    print("-" * 80)
    
    for idx, row in df.iterrows():
        question = row['Question']
        expected = row.get('Expected Answer', '')
        
        # Router et exécuter
        route = router.route(question)
        response = agents[route].run(question) if route in agents else ""
        
        # Évaluer avec LLM
        score = judge.score(question, expected, response)
        
        results.append({
            'id': idx+1,
            'question': question,
            'route': route,
            'response': response[:200],
            'expected': str(expected)[:200],
            'score': score
        })
        
        # Afficher résultat
        status = "✓" if score >= 2 else "✗"
        score_symbol = ["🔴", "🟠", "🟡", "🟢"][score]
        print(f"[{idx+1:2d}/{len(df)}] {status} [{route:4s}] {score_symbol} Score: {score}/3")
    
    # Statistiques
    df_results = pd.DataFrame(results)
    avg_score = df_results['score'].mean()
    
    print("\n" + "=" * 80)
    print("📊 RÉSULTATS FINAUX")
    print("=" * 80)
    print(f"🎯 Score moyen: {avg_score:.2f}/3")
    print(f"🏆 Score total: {df_results['score'].sum()}/{len(df)*3}")
    
    # Distribution des scores
    print("\n📊 Distribution des scores:")
    for i in range(4):
        count = len(df_results[df_results['score'] == i])
        percent = (count / len(df_results)) * 100
        bar = "█" * int(percent / 5)
        print(f"  {i}/3: {count:2d} questions ({percent:5.1f}%) {bar}")
    
    # Par agent
    print("\n📈 Performance par agent:")
    for route in df_results['route'].unique():
        route_data = df_results[df_results['route'] == route]
        avg = route_data['score'].mean()
        print(f"  {route}: {avg:.2f}/3 ({len(route_data)} questions)")
    
    # Questions avec bas score
    low_scores = df_results[df_results['score'] <= 1]
    if len(low_scores) > 0:
        print(f"\n⚠️  Questions à améliorer (score ≤ 1):")
        for _, row in low_scores.iterrows():
            print(f"  Q{row['id']:02d}: {row['question'][:60]}...")
    
    # Sauvegarder
    df_results.to_csv('llm_evaluation.csv', index=False, encoding='utf-8')
    print(f"\n💾 Résultats sauvegardés dans: llm_evaluation.csv")
    
    return df_results

if __name__ == "__main__":
    evaluate()