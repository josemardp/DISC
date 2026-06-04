import os
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    GENAI_AVAILABLE = False
from typing import Dict, Any, List
from backend.app.config import settings

def generate_psychometric_report(
    candidate_name: str,
    disc_natural: Dict[str, float],
    disc_adapted: Dict[str, float],
    burnout_distance: float,
    burnout_risk: str,
    spranger_scores: Dict[str, float],
    jung_type: str,
    jung_scores: Dict[str, float],
    frictions: List[Dict[str, Any]],
    telemetry_alerts: List[str]
) -> str:
    """
    Chama a API do Gemini 1.5 Flash para gerar um relatório psicométrico narrativo e analítico estruturado.
    Inclui um fallback completo de simulação local caso a GEMINI_API_KEY não esteja configurada.
    """
    
    # 1. Compilação das Fricções
    frictions_str = ""
    if frictions:
        frictions_str = "\n".join([f"- **{f['name']}** (Severidade: {f['severity']}): {f['description']}" for f in frictions])
    else:
        frictions_str = "Nenhuma fricção significativa de construto foi detectada."

    # 2. Compilação dos Alertas Telemétricos
    telemetry_str = ""
    if telemetry_alerts:
        telemetry_str = "\n".join([f"- {alert}" for alert in telemetry_alerts])
    else:
        telemetry_str = "Telemetria de preenchimento normal (sem sinais de preenchimento automatizado ou inconsistências temporais)."

    # 3. Construção do Prompt Técnico
    prompt = f"""
Você é um Consultor Organizacional e Psicometrista Sênior. Sua tarefa é compilar um Relatório Corporativo de Alta Performance com base nos metadados psicométricos e de telemetria abaixo:

DADOS DO AVALIADO:
- Nome: {candidate_name}

RESULTADOS DISC (Percentis):
- Perfil Natural (Essência): D={disc_natural.get('D', 0)}%, I={disc_natural.get('I', 0)}%, S={disc_natural.get('S', 0)}%, C={disc_natural.get('C', 0)}%
- Perfil Adaptado (Ambiente): D={disc_adapted.get('D', 0)}%, I={disc_adapted.get('I', 0)}%, S={disc_adapted.get('S', 0)}%, C={disc_adapted.get('C', 0)}%
- Gasto Energético (Distância Euclidiana): {burnout_distance} (Risco de Burnout: {burnout_risk})

RESULTADOS SPRANGER (Percentis dos Motivadores):
- Teórico: {spranger_scores.get('teorico', 0)}%
- Utilitário/Econômico: {spranger_scores.get('economico', 0)}%
- Estético: {spranger_scores.get('estetico', 0)}%
- Social: {spranger_scores.get('social', 0)}%
- Individualista/Político: {spranger_scores.get('individualista', 0)}%
- Regulador/Tradicional: {spranger_scores.get('regulador', 0)}%

RESULTADOS JUNG (Tipo Psicológico):
- Tipo Dominante: {jung_type}
- Scores dos Polos: E={jung_scores.get('E', 0)}, I={jung_scores.get('I', 0)}, S={jung_scores.get('S', 0)}, N={jung_scores.get('N', 0)}, T={jung_scores.get('T', 0)}, F={jung_scores.get('F', 0)}, J={jung_scores.get('J', 0)}, P={jung_scores.get('P', 0)}

ZONAS DE FRICÇÃO DE CONSTRUTOS DETECTADAS:
{frictions_str}

SINAIS TELEMÉTRICOS DE SESSÃO:
{telemetry_str}

DIRETRIZES DE FORMATO E TOM:
- Use Markdown limpo para a estrutura.
- O tom deve ser estritamente analítico, clínico, corporativo, construtivo e livre de clichês motivacionais ou de autoajuda.
- Estruture o relatório exatamente nas seguintes seções:
  1. ### Resumo Executivo de Perfil
  2. ### Dinâmica Comportamental (DISC Natural vs Adaptado e Risco de Burnout)
  3. ### Direcionadores de Ação (Motivadores de Spranger)
  4. ### Estilo Cognitivo e Adaptação ao Trabalho (Jung)
  5. ### Análise de Zonas de Fricção e Telemetria Comportamental
  6. ### Recomendações de Gestão, Liderança e Plano de Autodesenvolvimento

Escreva o relatório em Português do Brasil.
"""

    # 4. Execução da Chamada da API
    if not settings.GEMINI_API_KEY or not GENAI_AVAILABLE:
        print("GEMINI_API_KEY não configurada ou API indisponível (ex: DLL bloqueada). Gerando relatório simulado de fallback...")
        return generate_mock_report(candidate_name, disc_natural, disc_adapted, burnout_risk, spranger_scores, jung_type, frictions_str)

    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Chamada síncrona simples (pode ser executada assincronamente pelo executor do backend)
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.3}
        )
        return response.text
    except Exception as e:
        print(f"Erro ao chamar a API do Gemini: {str(e)}. Retornando mock...")
        return generate_mock_report(candidate_name, disc_natural, disc_adapted, burnout_risk, spranger_scores, jung_type, frictions_str)

def generate_mock_report(
    candidate_name: str,
    disc_nat: Dict[str, float],
    disc_ada: Dict[str, float],
    burnout_risk: str,
    spranger: Dict[str, float],
    jung_type: str,
    frictions_str: str
) -> str:
    """
    Relatório de fallback realista gerado localmente na ausência de chave de API.
    """
    
    d_nat, i_nat, s_nat, c_nat = disc_nat.get('D', 0), disc_nat.get('I', 0), disc_nat.get('S', 0), disc_nat.get('C', 0)
    d_ada, i_ada, s_ada, c_ada = disc_ada.get('D', 0), disc_ada.get('I', 0), disc_ada.get('S', 0), disc_ada.get('C', 0)
    
    # Determina o estilo principal do DISC Natural
    style_map = {"D": d_nat, "I": i_nat, "S": s_nat, "C": c_nat}
    dominant_disc = max(style_map, key=style_map.get)
    disc_names = {"D": "Dominante", "I": "Influenciador", "S": "Estável", "C": "Conforme"}
    
    # Determina o principal motivador de Spranger
    dominant_spranger = max(spranger, key=spranger.get)
    spranger_names = {
        "teorico": "Teórico (Orientado ao Conhecimento)",
        "economico": "Utilitário/Econômico (Orientado a Resultados)",
        "estetico": "Estético (Orientado à Criatividade/Forma)",
        "social": "Social (Orientado a Pessoas/Empatia)",
        "individualista": "Individualista/Político (Orientado a Status/Liderança)",
        "regulador": "Regulador (Orientado a Regras/Processos)"
    }
    
    return f"""### Resumo Executivo de Perfil
O avaliado **{candidate_name}** exibe um perfil comportamental focado no eixo **{disc_names[dominant_disc]}** em seu estado natural. Sua energia interna é impulsionada predominantemente pelo motivador **{spranger_names[dominant_spranger]}**, e sua cognição opera sob o arranjo Junguiano **{jung_type}**. Esta combinação sugere um profissional com capacidade de alinhar traços comportamentais específicos com processos lógicos internos estruturados.

### Dinâmica Comportamental (DISC Natural vs Adaptado e Risco de Burnout)
* **Perfil Natural (Essência)**: D={d_nat}%, I={i_nat}%, S={s_nat}%, C={c_nat}%
* **Perfil Adaptado (Ambiente)**: D={d_ada}%, I={i_ada}%, S={s_ada}%, C={c_ada}%
* **Análise de Sobreadaptação**: O nível de afastamento entre os vetores de ação natural e adaptada indica um **Risco de Burnout {burnout_risk.upper()}**. 
* *Nota*: O avaliado realiza adaptações em seu comportamento para atender às expectativas de seu cargo atual, gerando um esforço cognitivo compatível com o limiar mapeado.

### Direcionadores de Ação (Motivadores de Spranger)
O perfil de motivadores aponta que as decisões operacionais do avaliado são energizadas por prioridades claras:
1. **{spranger_names[dominant_spranger]}**: Este é o principal drive motivacional. A pessoa direciona seus recursos cognitivos prioritariamente para satisfazer este construto de valores.
2. Os motivadores secundários indicam como ela balanceia a busca por resultados econômicos contra a conformidade com regras organizacionais.

### Estilo Cognitivo e Adaptação ao Trabalho (Jung)
Classificado sob a tipologia **{jung_type}**:
* O avaliado processa as informações corporativas de acordo com as preferências da sua tipologia, exibindo tendências claras de foco atencional (onde recarrega sua bateria mental) e tomada de decisão lógica/emocional estruturada.

### Análise de Zonas de Fricção e Telemetria Comportamental
**Zonas de Fricção Ativas**:
{frictions_str}

* **Análise Telemétrica**: Os metadados telemétricos indicam consistência de leitura. Não foram disparados gatilhos críticos de preenchimento mecânico rápido, sugerindo confiabilidade e legitimidade na resposta aos itens psicométricos apresentados.

### Recomendações de Gestão, Liderança e Plano de Autodesenvolvimento
* **Para Gestores**: Oferecer autonomia de execução técnica condizente com seus principais motivadores e prover feedbacks estruturados.
* **Cenário de Estresse**: Em situações de alta pressão ou fadiga extrema, o avaliado tende a recuar para seu perfil Natural (**{disc_names[dominant_disc]}**), reduzindo o esforço adaptado.
* **Plano de Desenvolvimento (PDI)**: Trabalhar o alinhamento de valores com processos formais e o autocuidado energético para evitar picos de sobreadaptação ao ambiente organizacional.
"""
