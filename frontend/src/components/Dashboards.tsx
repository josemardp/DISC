import React, { useState, useEffect } from "react";
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  ScatterChart, Scatter, LabelList, Cell, AreaChart, Area
} from "recharts";
import {
  User, Users, Shield, Briefcase, Plus, TrendingUp, AlertTriangle,
  FileText, Award, Layers, Zap, Info, HelpCircle, RotateCcw, Printer, BookOpen, Pencil
} from "lucide-react";

interface DashboardsProps {
  token: string;
  apiBaseUrl: string;
  userRole: string;
  onRetake?: () => void;
}

export default function Dashboards({ token, apiBaseUrl, userRole, onRetake }: DashboardsProps) {
  const [activeTab, setActiveTab] = useState<"self" | "rh" | "admin">("self");

  // Estado Geral
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 1. Dados de Autodesenvolvimento (Avaliados)
  const [selfData, setSelfData] = useState<any>(null);
  const [narrativeReport, setNarrativeReport] = useState<string | null>(null);
  const [loadingReport, setLoadingReport] = useState(false);
  const [printError, setPrintError] = useState<string | null>(null);
  const [editingReflections, setEditingReflections] = useState(false);
  const [savingReflections, setSavingReflections] = useState(false);
  const [reflectionError, setReflectionError] = useState<string | null>(null);
  const [reflectionSuccess, setReflectionSuccess] = useState<string | null>(null);
  const [reflectionDraft, setReflectionDraft] = useState({
    self_understanding_goal: "",
    current_pattern_to_observe: ""
  });

  // 2. Dados da area administrativa
  const [jobs, setJobs] = useState<any[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null);
  const [jobRankings, setJobRankings] = useState<any[]>([]);
  const [teamMatrix, setTeamMatrix] = useState<any[]>([]);
  const [showNewJobModal, setShowNewJobModal] = useState(false);
  
  // Form de perfil de referencia
  const [newJob, setNewJob] = useState({
    title: "",
    description: "",
    target_d: 0.5,
    target_i: 0.5,
    target_s: 0.5,
    target_c: 0.5,
    target_teorico: 50,
    target_economico: 50,
    target_estetico: 50,
    target_social: 50,
    target_individualista: 50,
    target_regulador: 50,
    target_E_I: 50,
    target_S_N: 50,
    target_T_F: 50,
    target_J_P: 50
  });

  // 3. Dados de Admin
  const [adminStats, setAdminStats] = useState<any>(null);

  // Inicializa visualização de abas permitidas
  useEffect(() => {
    if (userRole === "hr" || userRole === "admin") {
      setActiveTab("rh");
    } else {
      setActiveTab("self");
    }
  }, [userRole]);

  // Carrega dados da Tab ativa
  useEffect(() => {
    setError(null);
    if (activeTab === "self") {
      loadSelfData();
    } else if (activeTab === "rh") {
      loadRHData();
    } else if (activeTab === "admin") {
      loadAdminData();
    }
  }, [activeTab]);

  // Carrega comparativos ao mudar perfil selecionado
  useEffect(() => {
    if (selectedJobId) {
      loadJobRankings(selectedJobId);
    }
  }, [selectedJobId]);

  // ==============================================================================
  // CARREGADORES DE DADOS (API CHAT)
  // ==============================================================================

  const loadSelfData = () => {
    setLoading(true);
    fetch(`${apiBaseUrl}/results/me`, {
      headers: { "Authorization": `Bearer ${token}` }
    })
      .then(res => {
        if (!res.ok) throw new Error("Ainda não há avaliações concluídas.");
        return res.json();
      })
      .then(data => {
        setSelfData(data);
        setEditingReflections(false);
        setReflectionError(null);
        setReflectionSuccess(null);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  };

  const loadNarrativeReport = () => {
    setLoadingReport(true);
    fetch(`${apiBaseUrl}/results/report`, {
      headers: { "Authorization": `Bearer ${token}` }
    })
      .then(res => {
        if (!res.ok) throw new Error("Falha ao gerar relatório.");
        return res.json();
      })
      .then(data => {
        setNarrativeReport(data.report);
        setLoadingReport(false);
      })
      .catch(() => {
        setLoadingReport(false);
      });
  };

  const loadRHData = () => {
    setLoading(true);
    // Perfis de referencia
    fetch(`${apiBaseUrl}/rh/jobs`, {
      headers: { "Authorization": `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(jobsData => {
        setJobs(jobsData);
        if (jobsData.length > 0) {
          setSelectedJobId(jobsData[0].id);
        }
      })
      .catch(err => console.error(err));

    // Mapa térmico
    fetch(`${apiBaseUrl}/rh/team-matrix`, {
      headers: { "Authorization": `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(matrix => {
        setTeamMatrix(matrix);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  };

  const loadJobRankings = (jobId: number) => {
    fetch(`${apiBaseUrl}/rh/matching/${jobId}`, {
      headers: { "Authorization": `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(rankings => {
        setJobRankings(rankings);
      })
      .catch(err => console.error(err));
  };

  const loadAdminData = () => {
    setLoading(true);
    fetch(`${apiBaseUrl}/admin/stats`, {
      headers: { "Authorization": `Bearer ${token}` }
    })
      .then(res => {
        if (!res.ok) throw new Error("Acesso negado.");
        return res.json();
      })
      .then(data => {
        setAdminStats(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  };

  const handleCreateJob = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      title: newJob.title,
      description: newJob.description,
      target_d: newJob.target_d,
      target_i: newJob.target_i,
      target_s: newJob.target_s,
      target_c: newJob.target_c,
      target_spranger: {
        teorico: newJob.target_teorico,
        economico: newJob.target_economico,
        estetico: newJob.target_estetico,
        social: newJob.target_social,
        individualista: newJob.target_individualista,
        regulador: newJob.target_regulador
      },
      target_jung: {
        E: newJob.target_E_I,
        I: 100 - newJob.target_E_I,
        S: newJob.target_S_N,
        N: 100 - newJob.target_S_N,
        T: newJob.target_T_F,
        F: 100 - newJob.target_T_F,
        J: newJob.target_J_P,
        P: 100 - newJob.target_J_P
      }
    };

    try {
      const res = await fetch(`${apiBaseUrl}/rh/jobs`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error("Erro ao criar perfil de referência.");
      const jobCreated = await res.json();
      setJobs(prev => [...prev, jobCreated]);
      setSelectedJobId(jobCreated.id);
      setShowNewJobModal(false);
      setNewJob({
        title: "", description: "", target_d: 0.5, target_i: 0.5, target_s: 0.5, target_c: 0.5,
        target_teorico: 50, target_economico: 50, target_estetico: 50, target_social: 50, target_individualista: 50, target_regulador: 50,
        target_E_I: 50, target_S_N: 50, target_T_F: 50, target_J_P: 50
      });
    } catch (err: any) {
      alert(err.message);
    }
  };

  // ==============================================================================
  // AUXILIARES VISUAIS
  // ==============================================================================
  const getBurnoutColor = (risk: string) => {
    if (risk === "Alto") return "bg-red-500/20 text-red-300 border-red-500/30";
    if (risk === "Médio") return "bg-amber-500/20 text-amber-300 border-amber-500/30";
    return "bg-green-500/20 text-green-300 border-green-500/30";
  };

  // Prepara dados DISC para Radar Chart
  const getDiscRadarData = () => {
    if (!selfData) return [];
    return [
      { subject: "Dominância (D)", Natural: selfData.disc.natural.D, Adaptado: selfData.disc.adapted.D },
      { subject: "Influência (I)", Natural: selfData.disc.natural.I, Adaptado: selfData.disc.adapted.I },
      { subject: "Estabilidade (S)", Natural: selfData.disc.natural.S, Adaptado: selfData.disc.adapted.S },
      { subject: "Conformidade (C)", Natural: selfData.disc.natural.C, Adaptado: selfData.disc.adapted.C }
    ];
  };

  // Prepara dados Spranger para Bar Chart
  const getSprangerBarData = () => {
    if (!selfData) return [];
    return [
      { name: "Teórico", valor: selfData.spranger.teorico, fill: "#a78bfa" },
      { name: "Econômico", valor: selfData.spranger.economico, fill: "#34d399" },
      { name: "Estético", valor: selfData.spranger.estetico, fill: "#f472b6" },
      { name: "Social", valor: selfData.spranger.social, fill: "#38bdf8" },
      { name: "Individualista", valor: selfData.spranger.individualista, fill: "#fbbf24" },
      { name: "Regulador", valor: selfData.spranger.regulador, fill: "#fb7185" }
    ];
  };

  const getBigFiveFactors = () => {
    if (!selfData?.bigfive?.factors) return [];
    const order = ["O", "C", "E", "A", "N"];
    return order
      .filter((key) => selfData.bigfive.factors[key])
      .map((key) => ({ key, ...selfData.bigfive.factors[key] }));
  };

  const beginReflectionEdit = () => {
    setReflectionDraft({
      self_understanding_goal: selfData?.reflections?.self_understanding_goal || "",
      current_pattern_to_observe: selfData?.reflections?.current_pattern_to_observe || ""
    });
    setReflectionError(null);
    setReflectionSuccess(null);
    setEditingReflections(true);
  };

  const cancelReflectionEdit = () => {
    setEditingReflections(false);
    setReflectionError(null);
    setReflectionDraft({
      self_understanding_goal: selfData?.reflections?.self_understanding_goal || "",
      current_pattern_to_observe: selfData?.reflections?.current_pattern_to_observe || ""
    });
  };

  const saveReflections = async () => {
    if (!selfData?.result_id) {
      setReflectionError("Não foi possível identificar esta aplicação. Atualize a página e tente novamente.");
      return;
    }
    setSavingReflections(true);
    setReflectionError(null);
    setReflectionSuccess(null);
    try {
      const response = await fetch(`${apiBaseUrl}/results/${selfData.result_id}/reflections`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(reflectionDraft)
      });
      if (!response.ok) throw new Error("Falha ao atualizar reflexões.");
      const data = await response.json();
      setSelfData((previous: any) => ({ ...previous, reflections: data.reflections }));
      setReflectionDraft({
        self_understanding_goal: data.reflections?.self_understanding_goal || "",
        current_pattern_to_observe: data.reflections?.current_pattern_to_observe || ""
      });
      setEditingReflections(false);
      setReflectionSuccess("Suas reflexões foram atualizadas.");
    } catch {
      setReflectionError("Não foi possível salvar agora. Tente novamente.");
    } finally {
      setSavingReflections(false);
    }
  };

  const factorGuide: Record<string, { description: string; high: string; low: string; attentionHigh: string; attentionLow: string; practice: string }> = {
    O: {
      description: "Relacionada à curiosidade, imaginação, flexibilidade mental e interesse por novas ideias.",
      high: "Facilidade para explorar possibilidades, aprender por caminhos variados e imaginar alternativas.",
      low: "Preferência por caminhos conhecidos, critérios concretos e decisões mais ancoradas na experiência.",
      attentionHigh: "Muita abertura pode trazer dispersão se houver excesso de ideias sem priorização.",
      attentionLow: "Baixa abertura pode reduzir a disposição para experimentar soluções novas quando o contexto pede.",
      practice: "Reserve um pequeno espaço para testar uma ideia nova, mas defina um critério simples para decidir se ela continua."
    },
    C: {
      description: "Relacionada à organização, disciplina, responsabilidade e persistência.",
      high: "Boa tendência a planejar, cumprir combinados e sustentar esforço até concluir o que começou.",
      low: "Maior flexibilidade e espontaneidade, com possível preferência por ajustar o caminho enquanto anda.",
      attentionHigh: "Conscienciosidade muito alta pode virar rigidez ou autocobrança excessiva.",
      attentionLow: "Conscienciosidade mais baixa pode pedir apoio externo para rotina, prazos e continuidade.",
      practice: "Escolha uma tarefa importante e quebre em próximos passos pequenos, com horário realista para começar."
    },
    E: {
      description: "Relacionada à energia social, expressividade, busca por interação e iniciativa social.",
      high: "Maior facilidade para iniciar contato, verbalizar ideias e ganhar energia em interação.",
      low: "Maior tendência a preservar energia, refletir antes de se expor e preferir interações mais selecionadas.",
      attentionHigh: "Extroversão alta pode levar a agir ou falar rápido demais em momentos que pedem escuta.",
      attentionLow: "Extroversão baixa pode fazer boas ideias ficarem pouco visíveis para outras pessoas.",
      practice: "Observe em quais interações você ganha energia e em quais precisa de recuperação depois."
    },
    A: {
      description: "Relacionada à cooperação, empatia, confiança e cuidado com os outros.",
      high: "Boa tendência a cooperar, considerar sentimentos alheios e preservar vínculos.",
      low: "Maior franqueza, autonomia e disposição para questionar expectativas externas.",
      attentionHigh: "Amabilidade alta pode dificultar dizer não ou sustentar limites pessoais.",
      attentionLow: "Amabilidade mais baixa pode pedir cuidado extra com tom, escuta e negociação.",
      practice: "Antes de aceitar algo, pergunte: isto cabe na minha energia e nos meus limites atuais?"
    },
    N: {
      description: "Relacionada à sensibilidade ao estresse, preocupação e reatividade emocional.",
      high: "Maior sensibilidade para perceber riscos, tensões e sinais emocionais cedo.",
      low: "Maior estabilidade diante de pressão e tendência a se recuperar com mais facilidade.",
      attentionHigh: "Neuroticismo alto pode ampliar ruminação, preocupação e desgaste em fases intensas.",
      attentionLow: "Neuroticismo muito baixo pode reduzir a percepção de sinais sutis de incômodo ou risco.",
      practice: "Quando notar tensão, nomeie o que está sentindo e escolha uma ação pequena antes de decidir no impulso."
    }
  };

  const getFactorBasis = (factor: any) => {
    if (factor.percentile != null) return Number(factor.percentile);
    return Math.max(0, Math.min(100, Number(factor.mean ?? 0) * 20));
  };

  const getFactorLevel = (factor: any) => {
    const basis = getFactorBasis(factor);
    if (basis >= 67) return "high";
    if (basis <= 33) return "low";
    return "middle";
  };

  const getMostMarkedFactors = () => {
    return getBigFiveFactors()
      .map((factor: any) => ({ ...factor, basis: getFactorBasis(factor), distance: Math.abs(getFactorBasis(factor) - 50) }))
      .sort((a: any, b: any) => b.distance - a.distance)
      .slice(0, 2);
  };

  const getStrengths = () => {
    const marked = getMostMarkedFactors();
    if (marked.length === 0) return ["Ainda não há dados suficientes para destacar forças prováveis."];
    return marked.map((factor: any) => {
      const guide = factorGuide[factor.key];
      const level = getFactorLevel(factor);
      if (level === "middle") return `${factor.label}: nesta aplicação apareceu em faixa intermediária, sugerindo flexibilidade conforme o contexto.`;
      return `${factor.label}: ${level === "high" ? guide.high : guide.low}`;
    });
  };

  const getAttentionPoints = () => {
    const marked = getMostMarkedFactors();
    if (marked.length === 0) return ["Use este resultado como ponto de partida, não como conclusão final sobre você."];
    return marked.map((factor: any) => {
      const guide = factorGuide[factor.key];
      const level = getFactorLevel(factor);
      if (level === "middle") return `${factor.label}: observe em quais situações esse traço muda de intensidade.`;
      return `${factor.label}: ${level === "high" ? guide.attentionHigh : guide.attentionLow}`;
    });
  };

  const getResultContextText = () => {
    if (selfData?.bigfive?.is_first_assessment) {
      return "Esta é sua primeira aplicação. O sistema criou uma linha de base interna; a comparação intraindividual ficará mais útil a partir do reteste.";
    }
    if (selfData?.bigfive?.has_intraindividual_history) {
      return "A comparação mostra variações em relação à sua aplicação anterior. Pequenas mudanças podem refletir contexto do dia, cansaço, humor ou forma de responder.";
    }
    if (selfData?.bigfive?.has_population_norm) {
      return "A leitura usa uma norma pública exploratória. Ela ajuda a contextualizar tendências, mas não é norma brasileira validada.";
    }
    return "Suas respostas sugerem tendências para reflexão pessoal nesta aplicação.";
  };

  const getJungHelpText = () => {
    const type = selfData?.jung_continuo?.tipo_resumo;
    if (!type || type === "indefinido") {
      return "Os eixos ficaram próximos do centro. Isso não é um erro; apenas indica que o sistema não tem segurança suficiente para atribuir um tipo fechado nesta aplicação.";
    }
    return "Use esse resumo apenas como uma narrativa exploratória derivada do Big Five, não como uma tipagem fixa.";
  };

  const getHistoryEntries = () => {
    return Array.isArray(selfData?.history) ? selfData.history : [];
  };

  const formatHistoryDate = (value: string) => {
    if (!value) return "data não disponível";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "data não disponível";
    return date.toLocaleString("pt-BR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  };

  const getHistoryComparison = () => {
    const history = getHistoryEntries();
    if (history.length < 2) return [];
    const current = history[history.length - 1]?.bigfive_raw || {};
    const previous = history[history.length - 2]?.bigfive_raw || {};
    return ["O", "C", "E", "A", "N"].map((key) => {
      const currentValue = Number(current[key] ?? 0);
      const previousValue = Number(previous[key] ?? 0);
      const delta = currentValue - previousValue;
      const status = Math.abs(delta) <= 1 ? "estável" : delta > 1 ? "aumentou" : "reduziu";
      return {
        key,
        label: selfData?.bigfive?.factors?.[key]?.label || key,
        currentValue,
        previousValue,
        delta,
        status
      };
    });
  };

  const getComparisonByFactor = (factorKey: string) => {
    return getHistoryComparison().find((item: any) => item.key === factorKey);
  };

  const getDeltaClass = (status: string) => {
    if (status === "aumentou") return "border-emerald-400/20 bg-emerald-400/10 text-emerald-100";
    if (status === "reduziu") return "border-sky-400/20 bg-sky-400/10 text-sky-100";
    return "border-white/10 bg-white/5 text-gray-200";
  };

  const formatDelta = (delta: number) => {
    if (Math.abs(delta) <= 1) return "estável";
    return `${delta > 0 ? "+" : ""}${delta.toFixed(0)} pontos`;
  };

  const getVariationText = (status: string) => {
    if (status === "aumentou") return "respostas mais altas que na aplicação anterior";
    if (status === "reduziu") return "respostas mais baixas que na aplicação anterior";
    return "respostas próximas da aplicação anterior";
  };

  const getReportDate = () => {
    const latestHistory = getHistoryEntries()[getHistoryEntries().length - 1];
    return formatHistoryDate(selfData?.date || latestHistory?.created_at);
  };

  const formatPercentile = (value: number | null | undefined) => {
    if (value == null) return "linha de base interna";
    return `${Math.round(Number(value))}`;
  };

  const formatScore = (value: number | null | undefined) => {
    if (value == null || Number.isNaN(Number(value))) return "sem dado";
    return Number(value).toFixed(1);
  };

  const getPrintStatusText = (status: string) => {
    if (status === "aumentou") return "aumentou";
    if (status === "reduziu") return "reduziu";
    return "ficou estável";
  };

  const handlePrintReport = () => {
    if (!selfData?.bigfive) {
      setPrintError("Ainda não há dados suficientes para gerar o relatório.");
      return;
    }
    if (typeof window === "undefined" || typeof window.print !== "function") {
      setPrintError("Não foi possível abrir a janela de impressão neste navegador.");
      return;
    }
    setPrintError(null);
    window.setTimeout(() => {
      try {
        window.print();
      } catch {
        setPrintError("Não foi possível gerar o relatório agora. Tente novamente em instantes.");
      }
    }, 80);
  };

  const getQualityColor = (label: string) => {
    if (label === "baixa") return "bg-red-500/20 text-red-300 border-red-500/30";
    if (label === "media") return "bg-amber-500/20 text-amber-300 border-amber-500/30";
    return "bg-emerald-500/20 text-emerald-300 border-emerald-500/30";
  };

  const getJungAxes = () => {
    const axes = selfData?.jung_continuo?.eixos || {};
    return Object.entries(axes).map(([key, value]: any) => ({
      key,
      leftLabel: Object.keys(value).find((k) => k !== "borderline") || "",
      rightLabel: Object.keys(value).filter((k) => k !== "borderline")[1] || "",
      ...value
    }));
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Abas Superiores de Controle de Dashboard */}
      <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-8">
        <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-violet-300 to-indigo-100">
          Meu perfil de autoconhecimento
        </h1>

        <div className="flex bg-white/5 p-1 rounded-2xl border border-white/5">
          {selfData && (
            <button
              onClick={() => setActiveTab("self")}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition ${
                activeTab === "self" ? "bg-brand-600 text-white shadow-md shadow-brand-500/20" : "text-gray-400 hover:text-white"
              }`}
            >
              <User className="w-4 h-4" />
              Meu Perfil
            </button>
          )}

          {(userRole === "hr" || userRole === "admin") && (
            <button
              onClick={() => setActiveTab("rh")}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition ${
                activeTab === "rh" ? "bg-brand-600 text-white shadow-md shadow-brand-500/20" : "text-gray-400 hover:text-white"
              }`}
            >
              <Users className="w-4 h-4" />
              Área administrativa
            </button>
          )}

          {userRole === "admin" && (
            <button
              onClick={() => setActiveTab("admin")}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition ${
                activeTab === "admin" ? "bg-brand-600 text-white shadow-md shadow-brand-500/20" : "text-gray-400 hover:text-white"
              }`}
            >
              <Shield className="w-4 h-4" />
              Admin
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="p-6 bg-brand-900/10 border border-brand-500/20 rounded-3xl mb-8 text-center text-gray-300">
          <Info className="w-12 h-12 text-brand-400 mx-auto mb-3" />
          <p className="font-semibold text-lg text-white mb-1">Sem Dados Disponíveis</p>
          <p className="text-sm max-w-md mx-auto">{error}</p>
        </div>
      )}

      {loading && (
        <div className="flex flex-col items-center justify-center min-h-[300px] gap-4">
          <div className="w-12 h-12 border-4 border-brand-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-gray-400 text-sm">Carregando sua devolutiva...</p>
        </div>
      )}

      {!loading && !error && (
        <>
          {/* ==============================================================================
              TAB 1: MEU PERFIL (AUTODESENVOLVIMENTO)
              ============================================================================== */}
          {activeTab === "self" && selfData?.bigfive && (
            <div className="grid grid-cols-12 gap-6">
              <div className="col-span-12 glass-premium p-5 sm:p-6 rounded-3xl">
                <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-6">
                  <div>
                    <h3 className="text-lg font-bold text-white mb-1">Resumo geral do perfil</h3>
                    <p className="text-xs text-gray-400">{selfData.bigfive.norm_label}</p>
                  </div>
                  <div className="flex items-center gap-3 flex-wrap">
                    <span className={`w-fit px-3 py-1 rounded-full text-xs font-bold border ${getQualityColor(selfData.quality_label)}`}>
                      Qualidade {selfData.quality_label || "sem dado"}
                    </span>
                    <button
                      onClick={handlePrintReport}
                      className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-200 hover:text-white bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl transition"
                      title="Abrir janela para salvar o relatório como PDF"
                    >
                      <Printer className="w-3.5 h-3.5" />
                      Baixar relatório em PDF
                    </button>
                    {onRetake && (
                      <button
                        onClick={() => {
                          if (window.confirm("Iniciar uma nova rodada do teste? Seu resultado atual fica guardado.")) {
                            onRetake();
                          }
                        }}
                        className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-400 hover:text-white bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl transition"
                        title="Refazer teste"
                      >
                        <RotateCcw className="w-3.5 h-3.5" />
                        Refazer teste
                      </button>
                    )}
                  </div>
                </div>

                {printError && (
                  <div className="mb-5 rounded-2xl border border-red-400/20 bg-red-400/10 p-3 text-xs leading-relaxed text-red-100">
                    {printError}
                  </div>
                )}

                <div className="mb-5 rounded-2xl border border-amber-400/20 bg-amber-400/10 p-3 text-xs leading-relaxed text-amber-100">
                  {selfData.notice || "Este resultado é uma ferramenta de autoconhecimento e não constitui diagnóstico psicológico, laudo psicológico ou avaliação psicológica profissional."}
                </div>

                <div className="mb-6 grid grid-cols-1 lg:grid-cols-4 gap-4">
                  <div className="rounded-2xl border border-white/5 bg-white/[0.03] p-4">
                    <h4 className="text-sm font-bold text-white mb-2">O que apareceu nesta aplicação</h4>
                    <p className="text-xs leading-relaxed text-gray-300">
                      {getResultContextText()}
                    </p>
                  </div>
                  <div className="rounded-2xl border border-white/5 bg-white/[0.03] p-4">
                    <h4 className="text-sm font-bold text-white mb-2">Traços mais marcantes</h4>
                    <p className="text-xs leading-relaxed text-gray-300">
                      {getMostMarkedFactors().map((factor: any) => factor.label).join(", ") || "Aguardando dados suficientes para destacar traços."}
                    </p>
                  </div>
                  <div className="rounded-2xl border border-white/5 bg-white/[0.03] p-4">
                    <h4 className="text-sm font-bold text-white mb-2">Como usar agora</h4>
                    <p className="text-xs leading-relaxed text-gray-300">
                      Use este resultado como ponto de reflexão: observe em quais situações essas tendências ajudam, atrapalham ou mudam de intensidade.
                    </p>
                  </div>
                  <div className="rounded-2xl border border-amber-400/15 bg-amber-400/5 p-4">
                    <h4 className="text-sm font-bold text-white mb-2">Limites da avaliação</h4>
                    <p className="text-xs leading-relaxed text-gray-300">
                      Não é diagnóstico, laudo psicológico ou avaliação profissional. Ele organiza tendências desta aplicação para reflexão pessoal.
                    </p>
                  </div>
                </div>

                <div className="mb-6 grid grid-cols-1 xl:grid-cols-2 gap-4">
                  <div className="rounded-2xl border border-white/5 bg-white/[0.03] p-4">
                    <h4 className="text-sm font-bold text-white mb-2">Histórico de aplicações</h4>
                    <p className="text-xs leading-relaxed text-gray-300">
                      {getHistoryEntries().length <= 1
                        ? "Esta é a primeira aplicação salva. Ela funciona como linha de base interna para comparações futuras."
                        : `Você já tem ${getHistoryEntries().length} aplicações salvas para observar mudanças ao longo do tempo.`}
                    </p>
                    <div className="mt-3 space-y-2">
                      {getHistoryEntries().map((entry: any) => (
                        <div key={entry.id} className="flex flex-col gap-1 rounded-xl border border-white/5 bg-white/[0.03] px-3 py-2 sm:flex-row sm:items-center sm:justify-between">
                          <div>
                            <p className="text-xs font-semibold text-white">Aplicação {entry.sequence}</p>
                            <p className="text-[11px] text-gray-500">{formatHistoryDate(entry.created_at)}</p>
                          </div>
                          <span className="w-fit rounded-full border border-white/10 bg-white/5 px-2.5 py-1 text-[10px] font-semibold text-gray-300">
                            {entry.norm_label || "histórico interno"}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="rounded-2xl border border-white/5 bg-white/[0.03] p-4">
                    <h4 className="text-sm font-bold text-white mb-2">Comparação com a aplicação anterior</h4>
                    {getHistoryComparison().length === 0 ? (
                      <p className="text-xs leading-relaxed text-gray-300">
                        A comparação aparece a partir do reteste. Por enquanto, esta aplicação serve como referência inicial.
                      </p>
                    ) : (
                      <>
                        <p className="text-xs leading-relaxed text-gray-300">
                          Variação simples entre as duas aplicações mais recentes, usando os resultados brutos do Big Five.
                        </p>
                        <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-2">
                          {getHistoryComparison().map((item: any) => (
                            <div key={item.key} className={`rounded-xl border px-3 py-2 ${getDeltaClass(item.status)}`}>
                              <div className="flex items-center justify-between gap-3">
                                <span className="text-xs font-semibold">{item.label}</span>
                                <span className="shrink-0 text-[11px] font-bold">{formatDelta(item.delta)}</span>
                              </div>
                              <p className="mt-1 text-[11px] leading-relaxed opacity-85">{getVariationText(item.status)}</p>
                            </div>
                          ))}
                        </div>
                      </>
                    )}
                    <div className="mt-3 rounded-xl border border-amber-400/20 bg-amber-400/10 p-3 text-[11px] leading-relaxed text-amber-100">
                      Mudanças pequenas podem refletir contexto, cansaço, humor ou forma de responder. Use como pista de reflexão, não como conclusão definitiva.
                    </div>
                  </div>
                </div>

                <div className="mb-6 rounded-2xl border border-violet-400/20 bg-violet-400/5 p-4 sm:p-5">
                  <div className="flex items-start gap-3">
                    <BookOpen className="mt-0.5 h-5 w-5 shrink-0 text-violet-300" />
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                        <h4 className="text-sm font-bold text-white">Minhas reflexões</h4>
                        {!editingReflections && (
                          <button
                            type="button"
                            onClick={beginReflectionEdit}
                            className="flex w-fit items-center gap-1.5 rounded-xl border border-violet-300/20 bg-violet-300/10 px-3 py-2 text-xs font-semibold text-violet-100 transition hover:bg-violet-300/15"
                          >
                            <Pencil className="h-3.5 w-3.5" />
                            Editar minhas reflexões
                          </button>
                        )}
                      </div>
                      <p className="mt-1 text-xs leading-relaxed text-gray-400">
                        Estas respostas são pessoais e não alteram sua pontuação psicométrica.
                      </p>

                      {editingReflections ? (
                        <div className="mt-4 space-y-4">
                          <label className="block min-w-0">
                            <span className="text-xs font-semibold leading-relaxed text-violet-100">
                              O que você espera compreender melhor sobre si mesmo com este teste?
                            </span>
                            <textarea
                              value={reflectionDraft.self_understanding_goal}
                              onChange={(event) => setReflectionDraft(previous => ({ ...previous, self_understanding_goal: event.target.value }))}
                              maxLength={1000}
                              rows={4}
                              className="mt-2 w-full min-w-0 resize-y rounded-xl border border-white/10 bg-white/5 p-3 text-sm leading-relaxed text-white outline-none transition focus:border-violet-300/60 focus:ring-2 focus:ring-violet-400/20"
                            />
                            <span className="mt-1 block text-right text-[11px] text-gray-500">{reflectionDraft.self_understanding_goal.length}/1000</span>
                          </label>
                          <label className="block min-w-0">
                            <span className="text-xs font-semibold leading-relaxed text-violet-100">
                              Ao olhar para sua rotina atual, qual comportamento, padrão ou dificuldade você gostaria de observar com mais atenção nas próximas semanas?
                            </span>
                            <textarea
                              value={reflectionDraft.current_pattern_to_observe}
                              onChange={(event) => setReflectionDraft(previous => ({ ...previous, current_pattern_to_observe: event.target.value }))}
                              maxLength={1000}
                              rows={4}
                              className="mt-2 w-full min-w-0 resize-y rounded-xl border border-white/10 bg-white/5 p-3 text-sm leading-relaxed text-white outline-none transition focus:border-violet-300/60 focus:ring-2 focus:ring-violet-400/20"
                            />
                            <span className="mt-1 block text-right text-[11px] text-gray-500">{reflectionDraft.current_pattern_to_observe.length}/1000</span>
                          </label>

                          {reflectionError && (
                            <p className="rounded-xl border border-red-400/20 bg-red-400/10 p-3 text-xs leading-relaxed text-red-100" role="alert">
                              {reflectionError}
                            </p>
                          )}

                          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
                            <button
                              type="button"
                              onClick={cancelReflectionEdit}
                              disabled={savingReflections}
                              className="rounded-xl border border-white/10 px-4 py-2.5 text-xs font-semibold text-gray-300 transition hover:bg-white/5 hover:text-white disabled:opacity-50"
                            >
                              Cancelar
                            </button>
                            <button
                              type="button"
                              onClick={saveReflections}
                              disabled={savingReflections}
                              className="rounded-xl bg-violet-600 px-4 py-2.5 text-xs font-semibold text-white transition hover:bg-violet-500 disabled:opacity-50"
                            >
                              {savingReflections ? "Salvando..." : "Salvar reflexões"}
                            </button>
                          </div>
                        </div>
                      ) : (
                        <>
                          {selfData.reflections?.self_understanding_goal || selfData.reflections?.current_pattern_to_observe ? (
                            <dl className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
                              {selfData.reflections?.self_understanding_goal && (
                                <div className="min-w-0 rounded-xl border border-white/5 bg-white/[0.03] p-3">
                                  <dt className="text-xs font-semibold text-violet-200">O que eu queria compreender melhor</dt>
                                  <dd className="mt-2 whitespace-pre-wrap break-words text-xs leading-relaxed text-gray-300">{selfData.reflections.self_understanding_goal}</dd>
                                </div>
                              )}
                              {selfData.reflections?.current_pattern_to_observe && (
                                <div className="min-w-0 rounded-xl border border-white/5 bg-white/[0.03] p-3">
                                  <dt className="text-xs font-semibold text-violet-200">Padrão que quero observar</dt>
                                  <dd className="mt-2 whitespace-pre-wrap break-words text-xs leading-relaxed text-gray-300">{selfData.reflections.current_pattern_to_observe}</dd>
                                </div>
                              )}
                            </dl>
                          ) : (
                            <p className="mt-4 text-xs leading-relaxed text-gray-300">Você ainda não registrou reflexões pessoais para esta aplicação.</p>
                          )}
                          {reflectionSuccess && (
                            <p className="mt-3 rounded-xl border border-emerald-400/20 bg-emerald-400/10 p-3 text-xs text-emerald-100" role="status" aria-live="polite">
                              {reflectionSuccess}
                            </p>
                          )}
                        </>
                      )}
                    </div>
                  </div>
                </div>

                <div className="mb-6 grid grid-cols-1 lg:grid-cols-2 gap-4">
                  <div className="rounded-2xl border border-emerald-400/15 bg-emerald-400/5 p-4">
                    <h4 className="text-sm font-bold text-emerald-100 mb-3">Pontos fortes prováveis</h4>
                    <ul className="space-y-2 text-xs leading-relaxed text-gray-300">
                      {getStrengths().map((item, idx) => <li key={idx}>{item}</li>)}
                    </ul>
                  </div>
                  <div className="rounded-2xl border border-sky-400/15 bg-sky-400/5 p-4">
                    <h4 className="text-sm font-bold text-sky-100 mb-3">Pontos de atenção</h4>
                    <ul className="space-y-2 text-xs leading-relaxed text-gray-300">
                      {getAttentionPoints().map((item, idx) => <li key={idx}>{item}</li>)}
                    </ul>
                  </div>
                </div>

                <div className="mb-6 rounded-2xl border border-brand-400/15 bg-brand-400/5 p-4">
                  <h4 className="text-sm font-bold text-white mb-3">Sugestões práticas para o dia a dia</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs leading-relaxed text-gray-300">
                    {getMostMarkedFactors().map((factor: any) => (
                      <p key={factor.key}>{factorGuide[factor.key]?.practice}</p>
                    ))}
                    <p>Releia este resultado em outro dia e veja quais frases ainda parecem úteis. O objetivo é gerar conversa consigo mesmo, não fechar uma definição.</p>
                  </div>
                </div>

                <div className="mb-5">
                  <h3 className="text-base font-bold text-white mb-1">Big Five medido</h3>
                  <p className="text-xs leading-relaxed text-gray-400">
                    Os cinco fatores abaixo são o núcleo medido diretamente. As demais leituras da tela são derivadas ou exploratórias.
                  </p>
                </div>

                <div className="space-y-5">
                  {getBigFiveFactors().map((factor: any) => (
                    <div key={factor.key} className="space-y-2 rounded-2xl border border-white/5 bg-white/[0.03] p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="text-sm font-semibold text-white">{factor.label}</p>
                          <p className="text-[11px] leading-relaxed text-gray-400">{factorGuide[factor.key]?.description}</p>
                          <p className="mt-1 text-[11px] text-gray-500">média {Number(factor.mean ?? 0).toFixed(1)}/5 nesta aplicação</p>
                        </div>
                        <div className="shrink-0 text-right">
                          <p className="text-lg font-black text-brand-300">{Math.round(factor.raw)}/{factor.max_raw || 50}</p>
                          <p className="text-[11px] text-gray-500">resultado bruto</p>
                        </div>
                      </div>

                      <div className="w-full">
                        {factor.percentile == null ? (
                          <div className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-gray-300">
                            Linha de base interna criada; comparação intraindividual ainda não interpretável.
                          </div>
                        ) : (
                          <>
                            <div className="relative h-4 rounded-full bg-white/5 overflow-hidden">
                              {factor.ci_low != null && factor.ci_high != null && (
                                <div className="absolute top-0 h-full bg-white/10" style={{ left: `${factor.ci_low}%`, width: `${Math.max(1, factor.ci_high - factor.ci_low)}%` }} />
                              )}
                              <div className="h-full rounded-full bg-gradient-to-r from-brand-500 to-sky-400" style={{ width: `${factor.percentile}%` }} />
                            </div>
                            <div className="mt-1 flex justify-between text-[10px] text-gray-500">
                              <span>faixa provável {factor.ci_low}</span>
                              <span>{factor.ci_high}</span>
                            </div>
                          </>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="col-span-12 lg:col-span-5 glass p-5 sm:p-6 rounded-3xl">
                <div className="flex items-center justify-between gap-4 mb-5">
                  <div>
                    <h3 className="text-base font-bold text-white">Jung exploratório</h3>
                    <p className="text-[11px] text-gray-400">Leitura derivada do Big Five, sem tipagem fechada quando há dúvida.</p>
                  </div>
                  <div className="bg-brand-500/20 text-brand-300 font-bold border border-brand-500/30 text-xl px-4 py-2 rounded-2xl text-center">
                    {selfData.jung_continuo?.tipo_resumo || "indefinido"}
                  </div>
                </div>

                {selfData.jung_continuo?.aviso && (
                  <div className="mb-4 rounded-2xl border border-amber-400/20 bg-amber-400/10 p-3 text-xs leading-relaxed text-amber-100">
                    {selfData.jung_continuo.aviso}
                  </div>
                )}
                <p className="mb-4 text-xs leading-relaxed text-gray-300">{getJungHelpText()}</p>

                <div className="space-y-4">
                  {getJungAxes().map((axis: any) => (
                    <div key={axis.key}>
                      <div className="flex justify-between gap-3 text-xs font-semibold">
                        <span className="text-gray-300">{axis.leftLabel}: {axis[axis.leftLabel]}%</span>
                        <span className="text-gray-400">{axis.rightLabel}: {axis[axis.rightLabel]}%</span>
                      </div>
                      <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden flex mt-1.5">
                        <div className="h-full bg-brand-500" style={{ width: `${axis[axis.leftLabel]}%` }} />
                        <div className="h-full bg-sky-400" style={{ width: `${axis[axis.rightLabel]}%` }} />
                      </div>
                      {axis.borderline && <div className="mt-1 text-[10px] text-amber-300">Eixo em zona borderline.</div>}
                    </div>
                  ))}
                </div>
              </div>

              <div className="col-span-12 lg:col-span-3 glass p-5 sm:p-6 rounded-3xl flex flex-col justify-between">
                <div>
                  <h3 className="text-base font-bold text-white">Estabilidade Emocional</h3>
                  <p className="text-[11px] text-gray-400">Inverso do Neuroticismo: indica menor sensibilidade ao estresse quando aparece mais alta.</p>
                </div>
                <div className="py-8 text-center">
                  <div className="text-5xl font-black text-emerald-300">{Math.round(selfData.jung_continuo?.estabilidade_emocional || 0)}</div>
                  <div className="mt-3 h-2 bg-white/5 rounded-full overflow-hidden">
                    <div className="h-full bg-emerald-400" style={{ width: `${selfData.jung_continuo?.estabilidade_emocional || 0}%` }} />
                  </div>
                </div>
              </div>

              <div className="col-span-12 lg:col-span-4 glass p-5 sm:p-6 rounded-3xl">
                <h3 className="text-base font-bold text-white mb-2">DISC Derivado</h3>
                <p className="mb-4 text-[11px] leading-relaxed text-gray-400">
                  {selfData.disc?.aviso || "DISC derivado — leitura ilustrativa baseada nos fatores Big Five. Não substitui um instrumento DISC validado."}
                </p>
                <p className="mb-4 text-xs leading-relaxed text-gray-300">
                  Use como linguagem simples para refletir sobre estilo de ação, não como medida independente.
                </p>
                <div className="grid grid-cols-2 gap-3">
                  {Object.entries(selfData.disc.natural).map(([key, value]: any) => (
                    <div key={key} className="bg-white/5 rounded-2xl p-4 border border-white/5">
                      <div className="text-xs text-gray-400">{key}</div>
                      <div className="text-2xl font-black text-white">{Math.round(value)}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="col-span-12 glass p-5 sm:p-6 rounded-3xl">
                <h3 className="text-base font-bold text-white mb-2">Spranger Derivado</h3>
                <p className="mb-4 text-[11px] leading-relaxed text-gray-400">
                  {selfData.spranger?.aviso || "Spranger derivado — leitura ilustrativa baseada nos fatores Big Five. Não substitui um instrumento motivacional validado."}
                </p>
                <p className="mb-4 text-xs leading-relaxed text-gray-300">
                  Esta leitura sugere temas motivacionais possíveis a partir do Big Five, sem fechar valores ou identidade.
                </p>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                  {Object.entries(selfData.spranger)
                    .filter(([key]) => !["derived_from", "aviso"].includes(key))
                    .map(([key, value]: any) => (
                      <div key={key} className="bg-white/5 rounded-2xl p-4 border border-white/5">
                        <div className="text-xs text-gray-400 capitalize">{key}</div>
                        <div className="text-2xl font-black text-white">{Math.round(value)}</div>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === "self" && selfData && !selfData.bigfive && (
            <div className="grid grid-cols-12 gap-6">
              
              {/* Radar DISC */}
              <div className="col-span-12 lg:col-span-6 glass-premium p-6 rounded-3xl min-h-[380px] flex flex-col justify-between">
                <div>
                  <h3 className="text-lg font-bold text-white mb-1">Mapeamento DISC</h3>
                  <p className="text-xs text-gray-400 mb-4">Sobreposição das curvas de perfil Natural (Essência) e Adaptado (Ambiente).</p>
                </div>
                <div className="w-full h-[280px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart cx="50%" cy="50%" radius="75%" data={getDiscRadarData()}>
                      <PolarGrid stroke="rgba(255,255,255,0.05)" />
                      <PolarAngleAxis dataKey="subject" tick={{ fill: '#9ca3af', fontSize: 12 }} />
                      <PolarRadiusAxis angle={45} domain={[0, 100]} tick={{ fill: '#6b7280' }} />
                      <Radar name="Natural" dataKey="Natural" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.15} />
                      <Radar name="Adaptado" dataKey="Adaptado" stroke="#38bdf8" fill="#38bdf8" fillOpacity={0.15} />
                      <Tooltip contentStyle={{ backgroundColor: '#0f0c29', border: '1px solid rgba(255,255,255,0.1)' }} />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex items-center justify-center gap-6 text-xs mt-2 border-t border-white/5 pt-2">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-brand-500 rounded-sm" />
                    <span className="text-gray-300">Natural</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-sky-400 rounded-sm" />
                    <span className="text-gray-300">Adaptado</span>
                  </div>
                </div>
              </div>

              {/* Motivadores Spranger */}
              <div className="col-span-12 lg:col-span-6 glass-premium p-6 rounded-3xl min-h-[380px] flex flex-col justify-between">
                <div>
                  <h3 className="text-lg font-bold text-white mb-1">Motivadores e Direcionadores (Spranger)</h3>
                  <p className="text-xs text-gray-400 mb-4">Hierarquia de impulsos de energia e tomada de decisões.</p>
                </div>
                <div className="w-full h-[280px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={getSprangerBarData()} layout="vertical" margin={{ left: 10, right: 10 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={true} vertical={false} />
                      <XAxis type="number" domain={[0, 100]} hide />
                      <YAxis dataKey="name" type="category" tick={{ fill: '#9ca3af', fontSize: 12 }} width={90} />
                      <Tooltip contentStyle={{ backgroundColor: '#0f0c29', border: '1px solid rgba(255,255,255,0.1)' }} />
                      <Bar dataKey="valor" radius={[0, 4, 4, 0]} barSize={16}>
                        {getSprangerBarData().map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.fill} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <span className="text-[10px] text-gray-500 uppercase tracking-widest text-center">Medição Populacional em Percentis</span>
              </div>

              {/* Jung Tipos Cognitivos */}
              <div className="col-span-12 lg:col-span-4 glass p-6 rounded-3xl flex flex-col justify-between">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-base font-bold text-white mb-0.5">Estilo de Jung</h3>
                    <p className="text-[11px] text-gray-400">Classificação cognitiva comportamental.</p>
                  </div>
                  <div className="bg-brand-500/20 text-brand-300 font-bold border border-brand-500/30 text-2xl px-4 py-2 rounded-2xl">
                    {selfData.jung.dominant_type}
                  </div>
                </div>

                <div className="flex flex-col gap-4">
                  {/* Extroversão vs Introversão */}
                  <div className="flex flex-col gap-1.5">
                    <div className="flex justify-between text-xs font-semibold">
                      <span className="text-gray-300">Extroversão (E): {selfData.jung.scores.E}%</span>
                      <span className="text-gray-400">Introversão (I): {selfData.jung.scores.I}%</span>
                    </div>
                    <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden flex">
                      <div className="h-full bg-brand-500" style={{ width: `${selfData.jung.scores.E}%` }} />
                      <div className="h-full bg-brand-300" style={{ width: `${selfData.jung.scores.I}%` }} />
                    </div>
                  </div>

                  {/* Sensação vs Intuição */}
                  <div className="flex flex-col gap-1.5">
                    <div className="flex justify-between text-xs font-semibold">
                      <span className="text-gray-300">Sensação (S): {selfData.jung.scores.S}%</span>
                      <span className="text-gray-400">Intuição (N): {selfData.jung.scores.N}%</span>
                    </div>
                    <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden flex">
                      <div className="h-full bg-brand-500" style={{ width: `${selfData.jung.scores.S}%` }} />
                      <div className="h-full bg-brand-300" style={{ width: `${selfData.jung.scores.N}%` }} />
                    </div>
                  </div>

                  {/* Pensamento vs Sentimento */}
                  <div className="flex flex-col gap-1.5">
                    <div className="flex justify-between text-xs font-semibold">
                      <span className="text-gray-300">Pensamento (T): {selfData.jung.scores.T}%</span>
                      <span className="text-gray-400">Sentimento (F): {selfData.jung.scores.F}%</span>
                    </div>
                    <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden flex">
                      <div className="h-full bg-brand-500" style={{ width: `${selfData.jung.scores.T}%` }} />
                      <div className="h-full bg-brand-300" style={{ width: `${selfData.jung.scores.F}%` }} />
                    </div>
                  </div>

                  {/* Julgamento vs Percepção */}
                  <div className="flex flex-col gap-1.5">
                    <div className="flex justify-between text-xs font-semibold">
                      <span className="text-gray-300">Julgamento (J): {selfData.jung.scores.J}%</span>
                      <span className="text-gray-400">Percepção (P): {selfData.jung.scores.P}%</span>
                    </div>
                    <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden flex">
                      <div className="h-full bg-brand-500" style={{ width: `${selfData.jung.scores.J}%` }} />
                      <div className="h-full bg-brand-300" style={{ width: `${selfData.jung.scores.P}%` }} />
                    </div>
                  </div>
                </div>
              </div>

              {/* Stress e Burnout */}
              <div className="col-span-12 lg:col-span-4 glass p-6 rounded-3xl flex flex-col justify-between">
                <div>
                  <h3 className="text-base font-bold text-white mb-0.5">Indicador de Burnout por Sobreadaptação</h3>
                  <p className="text-[11px] text-gray-400">Mapeamento de deslocamento vetorial temporal.</p>
                </div>

                <div className="flex items-center gap-4 py-3">
                  <div className={`p-4 border-2 rounded-2xl text-center flex flex-col shrink-0 ${getBurnoutColor(selfData.disc.burnout_risk)}`}>
                    <span className="text-[10px] uppercase font-bold tracking-widest text-gray-400">Risco</span>
                    <span className="text-xl font-black">{selfData.disc.burnout_risk}</span>
                  </div>
                  <div className="flex flex-col gap-1 text-sm">
                    <span className="text-gray-300">Distância Euclidiana: <strong className="text-white">{selfData.disc.burnout_distance}</strong></span>
                    <span className="text-xs text-gray-400">
                      Variação entre o que você é e o comportamento que está sendo exigido no momento no ambiente atual.
                    </span>
                  </div>
                </div>

                <div className="h-[1px] bg-white/5 my-2" />
                <span className="text-[10px] text-brand-300 flex items-center gap-1">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  Alerta crítico acima de 55 de distância.
                </span>
              </div>

              {/* Zonas de Fricção de Construto */}
              <div className="col-span-12 lg:col-span-4 glass p-6 rounded-3xl flex flex-col justify-between">
                <div>
                  <h3 className="text-base font-bold text-white mb-1">Atritos de Construtos Internos</h3>
                  <p className="text-[11px] text-gray-400">Pontos cegos no comportamento ou fadiga silenciosa.</p>
                </div>

                <div className="flex flex-col gap-3 max-h-[220px] overflow-y-auto pr-1">
                  {selfData.frictions.length === 0 ? (
                    <p className="text-xs text-green-300 bg-green-500/15 border border-green-500/20 p-4 rounded-2xl text-center">
                      Nenhuma fricção interna de comportamento ativa. Ótima fluidez cognitiva.
                    </p>
                  ) : (
                    selfData.frictions.map((f: any, idx: number) => (
                      <div key={idx} className="p-3 bg-red-900/15 border border-red-500/20 rounded-2xl">
                        <span className="text-xs font-bold text-red-300 block mb-0.5">{f.name}</span>
                        <p className="text-[10px] text-gray-400 leading-relaxed">{f.description}</p>
                      </div>
                    ))
                  )}
                </div>
                <div className="h-[1px] bg-white/5 my-2" />
                <span className="text-[10px] text-gray-500">Mapeamento DISC + Spranger + Jung cruzados.</span>
              </div>

              {/* Relatório narrativo pessoal */}
              <div className="col-span-12 glass-premium p-8 rounded-3xl mt-4">
                <div className="flex justify-between items-center mb-6">
                  <div className="flex items-center gap-3">
                    <FileText className="w-8 h-8 text-brand-400" />
                    <div>
                      <h3 className="text-xl font-bold text-white">Devolutiva pessoal guiada</h3>
                      <p className="text-xs text-gray-400">Resumo em linguagem natural para reflexão, sem valor de laudo ou diagnóstico.</p>
                    </div>
                  </div>

                  {!narrativeReport && (
                    <button
                      onClick={loadNarrativeReport}
                      disabled={loadingReport}
                      className="px-6 py-3 bg-white text-[#030014] font-semibold rounded-2xl hover:bg-gray-200 transition text-sm flex items-center gap-2 disabled:opacity-50"
                    >
                      {loadingReport ? (
                        <>
                          <div className="w-4 h-4 border-2 border-[#030014] border-t-transparent rounded-full animate-spin" />
                          Processando...
                        </>
                      ) : (
                        <>
                          Gerar devolutiva
                          <Zap className="w-4 h-4 fill-[#030014]" />
                        </>
                      )}
                    </button>
                  )}
                </div>

                <div className="h-[1px] bg-white/5 mb-6" />

                {narrativeReport ? (
                  <div className="prose prose-invert max-w-none text-gray-300 text-sm leading-relaxed whitespace-pre-line space-y-4">
                    {narrativeReport}
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-10 text-center text-gray-400">
                    <Award className="w-12 h-12 text-white/10 mb-3" />
                    <p className="text-sm max-w-xl">Ao clicar no botão superior, o sistema organiza os resultados em sete partes: resumo, traços marcantes, forças prováveis, pontos de atenção, sugestões práticas, uso no dia a dia e limites da avaliação.</p>
                  </div>
                )}
              </div>

            </div>
          )}

          {/* ==============================================================================
              TAB 2: AREA ADMINISTRATIVA
              ============================================================================== */}
          {activeTab === "rh" && (
            <div className="grid grid-cols-12 gap-6">
              
              {/* Painel Esquerdo: perfis de referencia e pessoas */}
              <div className="col-span-12 lg:col-span-7 flex flex-col gap-6">
                
                {/* Seletor de perfis de referencia */}
                <div className="glass-premium p-6 rounded-3xl">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                      <Briefcase className="w-5 h-5 text-brand-400" />
                      Perfis de referência
                    </h3>

                    <button
                      onClick={() => setShowNewJobModal(true)}
                      className="p-2 bg-brand-500/20 hover:bg-brand-500/30 text-brand-300 border border-brand-500/30 rounded-xl flex items-center gap-1 text-xs font-semibold transition"
                    >
                      <Plus className="w-4 h-4" />
                      Desenhar Perfil
                    </button>
                  </div>

                  {jobs.length === 0 ? (
                    <p className="text-sm text-gray-400 text-center py-6">Nenhum perfil de referência cadastrado.</p>
                  ) : (
                    <div className="flex flex-wrap gap-2">
                      {jobs.map((job) => (
                        <button
                          key={job.id}
                          onClick={() => setSelectedJobId(job.id)}
                          className={`px-4 py-2.5 rounded-xl border text-sm font-semibold transition ${
                            selectedJobId === job.id 
                              ? "bg-brand-600 border-brand-400 text-white shadow-md shadow-brand-500/20" 
                              : "bg-white/5 border-white/5 text-gray-400 hover:text-white"
                          }`}
                        >
                          {job.title}
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                {/* Lista de comparativos de pessoas */}
                <div className="glass-premium p-6 rounded-3xl min-h-[350px]">
                  <h3 className="text-lg font-bold text-white mb-4">Comparativo com perfil de referência</h3>

                  {jobRankings.length === 0 ? (
                    <p className="text-sm text-gray-400 text-center py-10">Selecione um perfil de referência para exibir a proximidade vetorial das pessoas.</p>
                  ) : (
                    <div className="space-y-4">
                      {jobRankings.map((cand, idx) => (
                        <div key={idx} className="glass p-4 rounded-2xl border-white/5 flex items-center justify-between hover:bg-white/[0.01] transition">
                          <div className="flex flex-col gap-1">
                            <strong className="text-white text-base">{cand.name}</strong>
                            <span className="text-xs text-gray-400">{cand.email} — Eixo de Jung: **{cand.dominant_type}**</span>
                          </div>

                          <div className="flex items-center gap-6">
                            {/* Burnout Risk Badge */}
                            <div className="flex flex-col items-end gap-1">
                              <span className="text-[10px] text-gray-500 uppercase tracking-widest">Burnout</span>
                              <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${getBurnoutColor(cand.burnout_risk)}`}>
                                {cand.burnout_risk}
                              </span>
                            </div>

                            {/* Score de Matching com Progresso */}
                            <div className="flex flex-col items-end gap-1">
                              <span className="text-xs text-gray-400">Proximidade vetorial</span>
                              <span className="text-xl font-black text-brand-300">{cand.matching_score}%</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

              </div>

              {/* Painel Direito: matriz de grupo */}
              <div className="col-span-12 lg:col-span-5 glass-premium p-6 rounded-3xl flex flex-col justify-between min-h-[480px]">
                <div>
                  <h3 className="text-lg font-bold text-white mb-1">Mapa de tendências do grupo</h3>
                  <p className="text-xs text-gray-400 mb-4">Visualização espacial de tendências atencionais e de execução.</p>
                </div>

                <div className="w-full h-[320px] bg-black/35 rounded-2xl border border-white/5 relative overflow-hidden">
                  {/* Grid Lines para o Quadrante */}
                  <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <div className="w-full h-[1px] bg-white/10" />
                    <div className="h-full w-[1px] bg-white/10" />
                  </div>
                  {/* Etiquetas de Quadrante */}
                  <div className="absolute top-2 left-2 text-[9px] font-bold text-gray-500 uppercase tracking-wider">Fast Pace / Pessoas</div>
                  <div className="absolute top-2 right-2 text-[9px] font-bold text-gray-500 uppercase tracking-wider">Fast Pace / Tarefas</div>
                  <div className="absolute bottom-2 left-2 text-[9px] font-bold text-gray-500 uppercase tracking-wider">Metódico / Pessoas</div>
                  <div className="absolute bottom-2 right-2 text-[9px] font-bold text-gray-500 uppercase tracking-wider">Metódico / Tarefas</div>

                  {teamMatrix.length === 0 ? (
                    <div className="flex items-center justify-center h-full text-sm text-gray-400">
                      Nenhuma pessoa mapeada na base.
                    </div>
                  ) : (
                    <ResponsiveContainer width="100%" height="100%">
                      <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                        <XAxis type="number" dataKey="x" name="Orientação" domain={[-50, 50]} hide />
                        <YAxis type="number" dataKey="y" name="Ritmo" domain={[-50, 50]} hide />
                        <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#0f0c29' }} />
                        <Scatter name="Time" data={teamMatrix} fill="#8b5cf6">
                          {teamMatrix.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.risk === "Alto" ? "#ef4444" : "#8b5cf6"} />
                          ))}
                          <LabelList dataKey="name" position="top" style={{ fill: '#ffffff', fontSize: 10, fontWeight: 500 }} />
                        </Scatter>
                      </ScatterChart>
                    </ResponsiveContainer>
                  )}
                </div>

                <div className="text-[10px] text-gray-500 leading-relaxed mt-2 text-center">
                  Pontos vermelhos indicam alto desvio entre modos de resposta e possível atenção a estresse.
                </div>
              </div>

            </div>
          )}

          {/* ==============================================================================
              TAB 3: PAINEL ADMINISTRADOR GLOBAL
              ============================================================================== */}
          {activeTab === "admin" && adminStats && (
            <div className="grid grid-cols-12 gap-6">
              
              {/* Métricas Globais */}
              <div className="col-span-12 sm:col-span-6 glass p-6 rounded-3xl flex items-center justify-between">
                <div>
                  <span className="text-xs text-gray-400 uppercase tracking-wider">Avaliações Totais</span>
                  <p className="text-4xl font-black text-white mt-1">{adminStats.total_evaluations}</p>
                </div>
                <div className="p-4 bg-brand-500/20 text-brand-300 rounded-2xl">
                  <Users className="w-8 h-8" />
                </div>
              </div>

              <div className="col-span-12 sm:col-span-6 glass p-6 rounded-3xl flex items-center justify-between">
                <div>
                  <span className="text-xs text-gray-400 uppercase tracking-wider">Ômega Big Five Médio</span>
                  <p className="text-4xl font-black text-emerald-400 mt-1">
                    {adminStats.omega_bigfive
                      ? (Object.values(adminStats.omega_bigfive).reduce((sum: number, value: any) => sum + Number(value || 0), 0) / 5).toFixed(2)
                      : "0.00"}
                  </p>
                </div>
                <div className="p-4 bg-emerald-500/20 text-emerald-300 rounded-2xl">
                  <TrendingUp className="w-8 h-8" />
                </div>
              </div>

              {/* Distribuição Gaussiana */}
              <div className="col-span-12 glass-premium p-6 rounded-3xl">
                <div className="flex items-center gap-2 mb-4">
                  <Layers className="w-5 h-5 text-brand-400" />
                  <h3 className="text-lg font-bold text-white">Curva de Distribuição Populacional (Eixo Dominância)</h3>
                </div>

                <div className="w-full h-[280px]">
                  {adminStats.gaussian.length === 0 ? (
                    <p className="text-sm text-gray-400 text-center py-20">Falta amostragem inicial para compilação da curva gaussiana global.</p>
                  ) : (
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={adminStats.gaussian}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                        <XAxis dataKey="x" tick={{ fill: '#9ca3af' }} />
                        <YAxis tick={{ fill: '#9ca3af' }} />
                        <Tooltip contentStyle={{ backgroundColor: '#0f0c29' }} />
                        <Area type="monotone" dataKey="y" stroke="#8b5cf6" fill="rgba(139, 92, 246, 0.15)" strokeWidth={2} />
                      </AreaChart>
                    </ResponsiveContainer>
                  )}
                </div>
                <div className="text-[10px] text-gray-500 text-center uppercase tracking-widest mt-2">
                  Eixo X: Nota Bruta (-24 a 24) — Eixo Y: Frequência Populacional
                </div>
              </div>

            </div>
          )}
        </>
      )}

      {selfData?.bigfive && (
        <article className="print-report" aria-label="Relatório pessoal de autoconhecimento">
          <section className="print-cover">
            <p className="print-kicker">Antigravity Psico</p>
            <h1>Relatório pessoal de autoconhecimento</h1>
            <p className="print-subtitle">
              Uma síntese exploratória das suas respostas nesta aplicação, com Big Five como núcleo medido e leituras derivadas apenas como apoio reflexivo.
            </p>
            <div className="print-meta-grid">
              <div>
                <span>Nome</span>
                <strong>{selfData.candidate || "Pessoa avaliada"}</strong>
              </div>
              <div>
                <span>Data da aplicação</span>
                <strong>{getReportDate()}</strong>
              </div>
              <div>
                <span>Modo de referência</span>
                <strong>{selfData.bigfive.norm_label}</strong>
              </div>
              <div>
                <span>Qualidade de resposta</span>
                <strong>{selfData.quality_label || "sem dado"}</strong>
              </div>
            </div>
            <div className="print-warning">
              {selfData.notice || "Este relatório é uma ferramenta de autoconhecimento e não constitui diagnóstico psicológico, laudo psicológico ou avaliação psicológica profissional."}
            </div>
          </section>

          <section className="print-section">
            <h2>1. Resumo geral</h2>
            <p>{getResultContextText()}</p>
            <p>
              Use este resultado como ponto de reflexão. Suas respostas sugerem tendências desta aplicação, que podem variar conforme contexto, energia, humor e forma de responder.
            </p>
          </section>

          <section className="print-section">
            <h2>2. Big Five medido</h2>
            <p>
              O Big Five é o núcleo medido diretamente. Na primeira aplicação em régua interna, o relatório não apresenta percentil interpretável; ele registra uma linha de base para comparações futuras.
            </p>
            <div className="print-factor-list">
              {getBigFiveFactors().map((factor: any) => {
                const comparison = getComparisonByFactor(factor.key);
                return (
                  <div key={factor.key} className="print-factor-card">
                    <div>
                      <h3>{factor.label}</h3>
                      <p>{factorGuide[factor.key]?.description}</p>
                    </div>
                    <dl>
                      <div>
                        <dt>Escore bruto</dt>
                        <dd>{Math.round(factor.raw)}/{factor.max_raw || 50}</dd>
                      </div>
                      <div>
                        <dt>Média por item</dt>
                        <dd>{formatScore(factor.mean)}/5</dd>
                      </div>
                      <div>
                        <dt>Percentil</dt>
                        <dd>{formatPercentile(factor.percentile)}</dd>
                      </div>
                      <div>
                        <dt>Variação</dt>
                        <dd>{comparison ? `${getPrintStatusText(comparison.status)} (${formatDelta(comparison.delta)})` : "sem reteste suficiente"}</dd>
                      </div>
                    </dl>
                  </div>
                );
              })}
            </div>
          </section>

          <section className="print-section print-two-columns">
            <div>
              <h2>3. Traços marcantes</h2>
              <p>{getMostMarkedFactors().map((factor: any) => factor.label).join(", ") || "Ainda não há dados suficientes para destacar traços."}</p>
            </div>
            <div>
              <h2>4. Pontos fortes prováveis</h2>
              <ul>
                {getStrengths().map((item, idx) => <li key={idx}>{item}</li>)}
              </ul>
            </div>
          </section>

          <section className="print-section print-two-columns">
            <div>
              <h2>5. Pontos de atenção</h2>
              <ul>
                {getAttentionPoints().map((item, idx) => <li key={idx}>{item}</li>)}
              </ul>
            </div>
            <div>
              <h2>6. Sugestões práticas</h2>
              <ul>
                {getMostMarkedFactors().map((factor: any) => (
                  <li key={factor.key}>{factorGuide[factor.key]?.practice}</li>
                ))}
                <li>Releia este resultado em outro dia e observe quais frases ainda parecem úteis.</li>
              </ul>
            </div>
          </section>

          <section className="print-section">
            <h2>7. Leituras derivadas</h2>
            <div className="print-derived-grid">
              <div>
                <h3>DISC derivado</h3>
                <p>{selfData.disc?.aviso || "DISC derivado — leitura ilustrativa baseada nos fatores Big Five. Não substitui um instrumento DISC validado."}</p>
                <p>
                  {Object.entries(selfData.disc?.natural || {})
                    .map(([key, value]: any) => `${key}: ${Math.round(value)}`)
                    .join(" · ")}
                </p>
              </div>
              <div>
                <h3>Jung exploratório</h3>
                <p>{getJungHelpText()}</p>
                <p>Resumo atual: {selfData.jung_continuo?.tipo_resumo || "indefinido"}</p>
              </div>
              <div>
                <h3>Spranger derivado</h3>
                <p>{selfData.spranger?.aviso || "Spranger derivado — leitura motivacional ilustrativa baseada no Big Five."}</p>
                <p>
                  {Object.entries(selfData.spranger || {})
                    .filter(([key]) => !["derived_from", "aviso"].includes(key))
                    .map(([key, value]: any) => `${key}: ${Math.round(value)}`)
                    .join(" · ")}
                </p>
              </div>
            </div>
          </section>

          <section className="print-section">
            <h2>8. Histórico e comparação</h2>
            {getHistoryEntries().length <= 1 ? (
              <p>Ainda não há histórico suficiente para comparação. Esta aplicação criou sua linha de base interna.</p>
            ) : (
              <>
                <div className="print-history-list">
                  {getHistoryEntries().map((entry: any) => (
                    <div key={entry.id}>
                      <strong>Aplicação {entry.sequence}</strong>
                      <span>{formatHistoryDate(entry.created_at)}</span>
                      <span>{entry.norm_label || "histórico interno"}</span>
                    </div>
                  ))}
                </div>
                <h3>Comparação com a aplicação anterior</h3>
                <ul>
                  {getHistoryComparison().map((item: any) => (
                    <li key={item.key}>
                      {item.label}: {getPrintStatusText(item.status)} ({formatDelta(item.delta)}).
                    </li>
                  ))}
                </ul>
              </>
            )}
            <p className="print-note">
              Mudanças pequenas podem refletir contexto do dia, humor, cansaço, ambiente ou forma de responder.
            </p>
          </section>

          <section className="print-section">
            <h2>9. Reflexões pessoais</h2>
            <p>Estas respostas foram escritas por você e não fazem parte da pontuação psicométrica.</p>
            {selfData.reflections?.self_understanding_goal || selfData.reflections?.current_pattern_to_observe ? (
              <dl className="print-reflections">
                {selfData.reflections?.self_understanding_goal && (
                  <div>
                    <dt>O que eu queria compreender melhor</dt>
                    <dd>{selfData.reflections.self_understanding_goal}</dd>
                  </div>
                )}
                {selfData.reflections?.current_pattern_to_observe && (
                  <div>
                    <dt>Padrão que quero observar</dt>
                    <dd>{selfData.reflections.current_pattern_to_observe}</dd>
                  </div>
                )}
              </dl>
            ) : (
              <p className="print-note">Nenhuma reflexão pessoal foi registrada nesta aplicação.</p>
            )}
          </section>

          <section className="print-section">
            <h2>10. Limites da avaliação</h2>
            <p>
              Este material não é diagnóstico, laudo psicológico, avaliação psicológica profissional, ferramenta de seleção ou resultado definitivo sobre personalidade.
            </p>
            <p>
              Jung, DISC e Spranger aparecem apenas como leituras derivadas/exploratórias. O objetivo é apoiar reflexão pessoal, não fechar identidade ou prever comportamento.
            </p>
          </section>
        </article>
      )}

      {/* ==============================================================================
          MODAL: DESENHAR PERFIL DE REFERENCIA
          ============================================================================== */}
      {showNewJobModal && (
        <div className="fixed inset-0 bg-black/85 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto">
          <div className="glass-premium max-w-2xl w-full p-8 rounded-3xl flex flex-col gap-6 max-h-[90vh] overflow-y-auto my-8">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-xl font-bold text-white">Desenhar perfil de referência</h3>
                <p className="text-xs text-gray-400">Configure um vetor comportamental e de motivadores para comparação exploratória.</p>
              </div>
              <button 
                onClick={() => setShowNewJobModal(false)}
                className="text-gray-400 hover:text-white font-bold text-sm px-3 py-1 bg-white/5 rounded-lg border border-white/5"
              >
                Fechar
              </button>
            </div>

            <form onSubmit={handleCreateJob} className="flex flex-col gap-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <label className="text-xs text-gray-400 font-bold block mb-1">Título do perfil</label>
                  <input
                    type="text"
                    required
                    value={newJob.title}
                    onChange={e => setNewJob(prev => ({ ...prev, title: e.target.value }))}
                    placeholder="Ex: perfil analítico, criativo ou executor"
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-brand-500"
                  />
                </div>
                <div className="col-span-2">
                  <label className="text-xs text-gray-400 font-bold block mb-1">Descrição</label>
                  <textarea
                    value={newJob.description}
                    onChange={e => setNewJob(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Descrição breve do contexto ou perfil de referência..."
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-brand-500 h-20"
                  />
                </div>
              </div>

              {/* Vetor DISC do perfil */}
              <div>
                <h4 className="text-sm font-bold text-brand-300 border-b border-white/5 pb-1 mb-3">Vetor Comportamental Ideal (DISC)</h4>
                <div className="grid grid-cols-4 gap-4">
                  <div>
                    <label className="text-xs text-gray-400 block mb-1">Dominância (D): {newJob.target_d * 100}%</label>
                    <input
                      type="range" min="0" max="1" step="0.1"
                      value={newJob.target_d}
                      onChange={e => setNewJob(prev => ({ ...prev, target_d: parseFloat(e.target.value) }))}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 block mb-1">Influência (I): {newJob.target_i * 100}%</label>
                    <input
                      type="range" min="0" max="1" step="0.1"
                      value={newJob.target_i}
                      onChange={e => setNewJob(prev => ({ ...prev, target_i: parseFloat(e.target.value) }))}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 block mb-1">Estabilidade (S): {newJob.target_s * 100}%</label>
                    <input
                      type="range" min="0" max="1" step="0.1"
                      value={newJob.target_s}
                      onChange={e => setNewJob(prev => ({ ...prev, target_s: parseFloat(e.target.value) }))}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 block mb-1">Conformidade (C): {newJob.target_c * 100}%</label>
                    <input
                      type="range" min="0" max="1" step="0.1"
                      value={newJob.target_c}
                      onChange={e => setNewJob(prev => ({ ...prev, target_c: parseFloat(e.target.value) }))}
                      className="w-full"
                    />
                  </div>
                </div>
              </div>

              {/* Motivadores Spranger */}
              <div>
                <h4 className="text-sm font-bold text-brand-300 border-b border-white/5 pb-1 mb-3">Motivadores do perfil (Intensidade 0-100)</h4>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="text-xs text-gray-400 block mb-1">Teórico: {newJob.target_teorico}</label>
                    <input
                      type="range" min="0" max="100"
                      value={newJob.target_teorico}
                      onChange={e => setNewJob(prev => ({ ...prev, target_teorico: parseInt(e.target.value) }))}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 block mb-1">Econômico: {newJob.target_economico}</label>
                    <input
                      type="range" min="0" max="100"
                      value={newJob.target_economico}
                      onChange={e => setNewJob(prev => ({ ...prev, target_economico: parseInt(e.target.value) }))}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 block mb-1">Estético: {newJob.target_estetico}</label>
                    <input
                      type="range" min="0" max="100"
                      value={newJob.target_estetico}
                      onChange={e => setNewJob(prev => ({ ...prev, target_estetico: parseInt(e.target.value) }))}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 block mb-1">Social: {newJob.target_social}</label>
                    <input
                      type="range" min="0" max="100"
                      value={newJob.target_social}
                      onChange={e => setNewJob(prev => ({ ...prev, target_social: parseInt(e.target.value) }))}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 block mb-1">Individualista: {newJob.target_individualista}</label>
                    <input
                      type="range" min="0" max="100"
                      value={newJob.target_individualista}
                      onChange={e => setNewJob(prev => ({ ...prev, target_individualista: parseInt(e.target.value) }))}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 block mb-1">Regulador: {newJob.target_regulador}</label>
                    <input
                      type="range" min="0" max="100"
                      value={newJob.target_regulador}
                      onChange={e => setNewJob(prev => ({ ...prev, target_regulador: parseInt(e.target.value) }))}
                      className="w-full"
                    />
                  </div>
                </div>
              </div>

              {/* Dicotomias Jung */}
              <div>
                <h4 className="text-sm font-bold text-brand-300 border-b border-white/5 pb-1 mb-3">Preferências junguianas do perfil</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs text-gray-400 block mb-1">Extroversão (E) vs Introversão (I): E={newJob.target_E_I}% / I={100 - newJob.target_E_I}%</label>
                    <input
                      type="range" min="0" max="100"
                      value={newJob.target_E_I}
                      onChange={e => setNewJob(prev => ({ ...prev, target_E_I: parseInt(e.target.value) }))}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 block mb-1">Sensação (S) vs Intuição (N): S={newJob.target_S_N}% / N={100 - newJob.target_S_N}%</label>
                    <input
                      type="range" min="0" max="100"
                      value={newJob.target_S_N}
                      onChange={e => setNewJob(prev => ({ ...prev, target_S_N: parseInt(e.target.value) }))}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 block mb-1">Pensamento (T) vs Sentimento (F): T={newJob.target_T_F}% / F={100 - newJob.target_T_F}%</label>
                    <input
                      type="range" min="0" max="100"
                      value={newJob.target_T_F}
                      onChange={e => setNewJob(prev => ({ ...prev, target_T_F: parseInt(e.target.value) }))}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400 block mb-1">Julgamento (J) vs Percepção (P): J={newJob.target_J_P}% / P={100 - newJob.target_J_P}%</label>
                    <input
                      type="range" min="0" max="100"
                      value={newJob.target_J_P}
                      onChange={e => setNewJob(prev => ({ ...prev, target_J_P: parseInt(e.target.value) }))}
                      className="w-full"
                    />
                  </div>
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-4 bg-gradient-to-r from-brand-600 to-indigo-600 text-white font-semibold rounded-2xl hover:from-brand-500 hover:to-indigo-500 transition duration-300"
              >
                Confirmar Desenho de Perfil
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
