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
    telemetry_alerts: List[str],
    bigfive_factors: Dict[str, Dict[str, float]] = None,
    jung_continuo: Dict[str, Any] = None,
    emotional_stability: float = None,
    quality_label: str = None
) -> str:
    """
    Chama a API do Gemini 1.5 Flash para gerar uma devolutiva pessoal estruturada.
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

    bigfive_factors = bigfive_factors or {}
    jung_continuo = jung_continuo or {}
    emotional_stability = emotional_stability if emotional_stability is not None else jung_continuo.get("estabilidade_emocional")
    quality_label = quality_label or "sem dados suficientes"

    factor_names = {
        "O": "Abertura",
        "C": "Conscienciosidade",
        "E": "Extroversão",
        "A": "Amabilidade",
        "N": "Neuroticismo",
    }
    if bigfive_factors:
        bigfive_str = "\n".join([
            (
                f"- {factor_names.get(key, key)} ({key}): escore={value.get('percentile', 'sem dados suficientes')}, "
                f"IC95%=[{value.get('ci_low', 'sem dados suficientes')}, {value.get('ci_high', 'sem dados suficientes')}], "
                f"bruto={value.get('raw', 'sem dados suficientes')}"
            )
            for key, value in bigfive_factors.items()
        ])
    else:
        bigfive_str = "- sem dados suficientes"

    jung_continuo_str = jung_continuo if jung_continuo else {
        "tipo_resumo": jung_type or "sem dados suficientes",
        "eixos": jung_scores or "sem dados suficientes",
        "estabilidade_emocional": emotional_stability or "sem dados suficientes",
    }

    # 3. Construção do prompt de devolutiva pessoal
    prompt = f"""
Você é um redator cuidadoso criando uma devolutiva pessoal de autoconhecimento em Português do Brasil. Use apenas os dados fornecidos; se faltar dado, diga "sem dados suficientes".

REGRAS OBRIGATÓRIAS ANTI-BARNUM:
- Use linguagem de incerteza: "suas respostas sugerem", "nesta aplicação apareceu", "pode indicar", "é possível que", "use como ponto de reflexão". Nunca escreva "você é", "o avaliado é" ou afirmações identitárias absolutas.
- Proíba frases genéricas que sirvam para qualquer pessoa, como "tem grande potencial", "busca equilíbrio", "às vezes é racional e às vezes emocional", "pode melhorar sob pressão" ou equivalentes sem vínculo direto com números.
- Cada interpretação precisa citar pelo menos um dado fornecido, especialmente escores e intervalos de confiança dos 5 fatores.
- Jung é apenas uma narrativa derivada do Big Five; nunca trate Jung como medida independente, diagnóstico ou tipo fixo.
- Inclua exatamente a seção "### Limites desta avaliação" com esta ideia explícita: "Este resultado é uma ferramenta de autoconhecimento e não constitui diagnóstico psicológico, laudo psicológico ou avaliação psicológica profissional."
- Não invente dados, referências, causas clínicas, histórico pessoal, traços não medidos ou recomendações sem base nos dados abaixo.

DADOS DO AVALIADO:
- Nome: {candidate_name}

BIG FIVE MEDIDO:
{bigfive_str}

JUNG CONTÍNUO DERIVADO DO BIG FIVE (apenas narrativa):
{jung_continuo_str}

ESTABILIDADE EMOCIONAL:
- {emotional_stability if emotional_stability is not None else "sem dados suficientes"}

QUALIDADE DA RESPOSTA:
- {quality_label}

DISC E SPRANGER DERIVADOS DO BIG FIVE (camadas de apresentação, não medidas independentes):
- DISC: D={disc_natural.get('D', 'sem dados suficientes')}, I={disc_natural.get('I', 'sem dados suficientes')}, S={disc_natural.get('S', 'sem dados suficientes')}, C={disc_natural.get('C', 'sem dados suficientes')}
- Spranger: {spranger_scores}
- INSTRUÇÃO: Spranger é uma estimativa ilustrativa derivada do Big Five, não um instrumento independente. Mencione isso brevemente ao apresentar os motivadores.

ZONAS DE FRICÇÃO DE CONSTRUTOS DETECTADAS:
{frictions_str}

SINAIS TELEMÉTRICOS DE SESSÃO:
{telemetry_str}

DIRETRIZES DE FORMATO E TOM:
- Use Markdown limpo para a estrutura.
- O tom deve ser humano, claro, útil e livre de clichês motivacionais ou linguagem de RH.
- Explique os fatores Big Five em linguagem simples.
- Se Jung vier indefinido, explique que isso não é erro: os eixos ficaram próximos do centro e não há segurança suficiente para tipo fechado.
- Estruture o relatório exatamente nas seguintes seções:
  1. ### Resumo geral do perfil
  2. ### Traços mais marcantes
  3. ### Pontos fortes prováveis
  4. ### Pontos de atenção
  5. ### Sugestões práticas
  6. ### Como usar esse resultado no dia a dia
  7. ### Limites desta avaliação
"""

    # 4. Execução da Chamada da API
    if not settings.GEMINI_API_KEY:
        print("GEMINI_API_KEY não configurada ou API indisponível (ex: DLL bloqueada). Gerando devolutiva local de fallback...")
        return generate_mock_report(
            candidate_name, disc_natural, disc_adapted, burnout_risk,
            spranger_scores, jung_type, frictions_str, bigfive_factors,
            jung_continuo, emotional_stability, quality_label
        )

    try:
        from google import genai
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=genai.types.GenerateContentConfig(temperature=0.3)
        )
        return response.text
    except Exception as e:
        print(f"Erro ao chamar a API do Gemini: {str(e)}. Retornando devolutiva local...")
        return generate_mock_report(
            candidate_name, disc_natural, disc_adapted, burnout_risk,
            spranger_scores, jung_type, frictions_str, bigfive_factors,
            jung_continuo, emotional_stability, quality_label
        )

def generate_mock_report(
    candidate_name: str,
    disc_nat: Dict[str, float],
    disc_ada: Dict[str, float],
    burnout_risk: str,
    spranger: Dict[str, float],
    jung_type: str,
    frictions_str: str,
    bigfive_factors: Dict[str, Dict[str, float]] = None,
    jung_continuo: Dict[str, Any] = None,
    emotional_stability: float = None,
    quality_label: str = None
) -> str:
    """
    Devolutiva de fallback gerada localmente na ausência de chave de API.
    """
    
    bigfive_factors = bigfive_factors or {}
    jung_continuo = jung_continuo or {}
    emotional_stability = emotional_stability if emotional_stability is not None else jung_continuo.get("estabilidade_emocional", "sem dados suficientes")
    quality_label = quality_label or "sem dados suficientes"

    factor_names = {
        "O": "Abertura",
        "C": "Conscienciosidade",
        "E": "Extroversão",
        "A": "Amabilidade",
        "N": "Neuroticismo",
    }
    factor_lines = []
    for key in ["O", "C", "E", "A", "N"]:
        factor = bigfive_factors.get(key, {})
        factor_lines.append(
            f"- **{factor_names[key]} ({key})**: comparação {factor.get('percentile', 'sem dados suficientes')}, "
            f"IC95% [{factor.get('ci_low', 'sem dados suficientes')}, {factor.get('ci_high', 'sem dados suficientes')}], "
            f"bruto {factor.get('raw', 'sem dados suficientes')}."
        )
    factor_text = "\n".join(factor_lines)

    tipo_resumo = jung_continuo.get("tipo_resumo", jung_type or "sem dados suficientes")
    eixos = jung_continuo.get("eixos", {})

    jung_note = (
        "Os eixos ficaram próximos do centro. Isso não é um erro; apenas indica que o sistema não tem segurança suficiente para atribuir um tipo fechado nesta aplicação."
        if tipo_resumo == "indefinido"
        else f"O resumo Jung **{tipo_resumo}** deve ser lido apenas como narrativa derivada do Big Five, não como medida independente nem tipo fixo."
    )

    return f"""### Resumo geral do perfil
Nesta aplicação, os dados de **{candidate_name}** sugerem tendências do Big Five que podem apoiar reflexão pessoal. A qualidade da resposta foi registrada como **{quality_label}**, então a leitura deve ser usada com cautela proporcional a esse indicador.

### Traços mais marcantes
{factor_text}

Esses dados sugerem tendências relativas dentro da régua disponível, mas não autorizam afirmações fixas de identidade. Abertura se relaciona a curiosidade e flexibilidade; Conscienciosidade a organização e persistência; Extroversão a energia social; Amabilidade a cooperação; Neuroticismo a sensibilidade ao estresse.

### Pontos fortes prováveis
Suas respostas podem indicar recursos úteis quando os fatores mais salientes são usados com intenção. Observe especialmente os fatores com maior distância da faixa central e veja em quais situações eles ajudam no dia a dia.

### Pontos de atenção
Fatores muito altos ou muito baixos podem pedir equilíbrio contextual. A Estabilidade Emocional derivada aparece como **{emotional_stability}**, que é o inverso do Neuroticismo; use essa leitura para observar sensibilidade ao estresse sem transformar isso em rótulo.

### Sugestões práticas
- Releia os fatores mais marcantes e escolha uma situação concreta da semana para observar.
- Compare o resultado com exemplos reais, não com uma imagem idealizada de si.
- Se alguma leitura incomodar ou parecer distante, trate como pergunta de reflexão, não como verdade final.

### Como usar esse resultado no dia a dia
{jung_note} DISC derivado: D={disc_nat.get('D', 'sem dados suficientes')}, I={disc_nat.get('I', 'sem dados suficientes')}, S={disc_nat.get('S', 'sem dados suficientes')}, C={disc_nat.get('C', 'sem dados suficientes')}. Spranger derivado: {spranger if spranger else "sem dados suficientes"}. Essas camadas são leituras ilustrativas baseadas no Big Five.

### Limites desta avaliação
Este resultado é uma ferramenta de autoconhecimento e não constitui diagnóstico psicológico, laudo psicológico ou avaliação psicológica profissional. Ele não descreve características imutáveis e não deve ser usado isoladamente para decisões de alto impacto.
"""
