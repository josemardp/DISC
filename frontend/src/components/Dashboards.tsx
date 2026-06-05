import React, { useState, useEffect } from "react";
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  ScatterChart, Scatter, LabelList, Cell, AreaChart, Area
} from "recharts";
import {
  User, Users, Shield, Briefcase, Plus, TrendingUp, AlertTriangle,
  FileText, Award, Layers, Zap, Info, HelpCircle
} from "lucide-react";

interface DashboardsProps {
  token: string;
  apiBaseUrl: string;
  userRole: string;
}

export default function Dashboards({ token, apiBaseUrl, userRole }: DashboardsProps) {
  const [activeTab, setActiveTab] = useState<"self" | "rh" | "admin">("self");

  // Estado Geral
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 1. Dados de Autodesenvolvimento (Avaliados)
  const [selfData, setSelfData] = useState<any>(null);
  const [narrativeReport, setNarrativeReport] = useState<string | null>(null);
  const [loadingReport, setLoadingReport] = useState(false);

  // 2. Dados de RH
  const [jobs, setJobs] = useState<any[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null);
  const [jobRankings, setJobRankings] = useState<any[]>([]);
  const [teamMatrix, setTeamMatrix] = useState<any[]>([]);
  const [showNewJobModal, setShowNewJobModal] = useState(false);
  
  // Form de Vaga
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

  // Carrega rankings ao mudar vaga selecionada
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
    // Vagas
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
      if (!res.ok) throw new Error("Erro ao criar vaga.");
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
          Resultados & Analytics
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
              Módulo RH
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
          <p className="text-gray-400 text-sm">Carregando métricas estatísticas...</p>
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
                    <h3 className="text-lg font-bold text-white mb-1">Big Five</h3>
                    <p className="text-xs text-gray-400">{selfData.bigfive.norm_label}</p>
                  </div>
                  <span className={`w-fit px-3 py-1 rounded-full text-xs font-bold border ${getQualityColor(selfData.quality_label)}`}>
                    Qualidade {selfData.quality_label || "sem dado"}
                  </span>
                </div>

                <div className="space-y-5">
                  {getBigFiveFactors().map((factor: any) => (
                    <div key={factor.key} className="grid grid-cols-12 gap-3 items-center">
                      <div className="col-span-12 sm:col-span-3">
                        <div className="text-sm font-semibold text-white">{factor.label}</div>
                        <div className="text-[11px] text-gray-500">{factor.key} bruto {factor.raw}</div>
                      </div>
                      <div className="col-span-12 sm:col-span-7">
                        <div className="relative h-4 rounded-full bg-white/5 overflow-hidden">
                          <div className="absolute top-0 h-full bg-white/10" style={{ left: `${factor.ci_low}%`, width: `${Math.max(1, factor.ci_high - factor.ci_low)}%` }} />
                          <div className="h-full rounded-full bg-gradient-to-r from-brand-500 to-sky-400" style={{ width: `${factor.percentile}%` }} />
                        </div>
                        <div className="mt-1 flex justify-between text-[10px] text-gray-500">
                          <span>IC {factor.ci_low}</span>
                          <span>{factor.ci_high}</span>
                        </div>
                      </div>
                      <div className="col-span-12 sm:col-span-2 text-left sm:text-right text-xl font-black text-brand-300">
                        {Math.round(factor.percentile)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="col-span-12 lg:col-span-5 glass p-5 sm:p-6 rounded-3xl">
                <div className="flex items-center justify-between gap-4 mb-5">
                  <div>
                    <h3 className="text-base font-bold text-white">Jung Contínuo</h3>
                    <p className="text-[11px] text-gray-400">Resumo derivado dos fatores Big Five.</p>
                  </div>
                  <div className="bg-brand-500/20 text-brand-300 font-bold border border-brand-500/30 text-2xl px-4 py-2 rounded-2xl">
                    {selfData.jung_continuo?.tipo_resumo}
                  </div>
                </div>

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
                  <p className="text-[11px] text-gray-400">Inverso do Neuroticismo.</p>
                </div>
                <div className="py-8 text-center">
                  <div className="text-5xl font-black text-emerald-300">{Math.round(selfData.jung_continuo?.estabilidade_emocional || 0)}</div>
                  <div className="mt-3 h-2 bg-white/5 rounded-full overflow-hidden">
                    <div className="h-full bg-emerald-400" style={{ width: `${selfData.jung_continuo?.estabilidade_emocional || 0}%` }} />
                  </div>
                </div>
              </div>

              <div className="col-span-12 lg:col-span-4 glass p-5 sm:p-6 rounded-3xl">
                <h3 className="text-base font-bold text-white mb-4">DISC Derivado</h3>
                <div className="grid grid-cols-2 gap-3">
                  {Object.entries(selfData.disc.natural).map(([key, value]: any) => (
                    <div key={key} className="bg-white/5 rounded-2xl p-4 border border-white/5">
                      <div className="text-xs text-gray-400">{key}</div>
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

              {/* Relatório Narrativo da IA (Streaming/Gemini) */}
              <div className="col-span-12 glass-premium p-8 rounded-3xl mt-4">
                <div className="flex justify-between items-center mb-6">
                  <div className="flex items-center gap-3">
                    <FileText className="w-8 h-8 text-brand-400" />
                    <div>
                      <h3 className="text-xl font-bold text-white">Relatório Narrativo Completo</h3>
                      <p className="text-xs text-gray-400">Análise gerada por Inteligência Artificial estatística e clínica.</p>
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
                          Gerar Relatório por IA
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
                    <p className="text-sm">Ao clicar no botão superior, a API do Gemini processará todos os dados estatísticos para gerar o relatório narrativo estruturado de competências.</p>
                  </div>
                )}
              </div>

            </div>
          )}

          {/* ==============================================================================
              TAB 2: GESTÃO DE RH / GESTORES
              ============================================================================== */}
          {activeTab === "rh" && (
            <div className="grid grid-cols-12 gap-6">
              
              {/* Painel Esquerdo: Vagas e Candidatos */}
              <div className="col-span-12 lg:col-span-7 flex flex-col gap-6">
                
                {/* Seletor de Vagas */}
                <div className="glass-premium p-6 rounded-3xl">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                      <Briefcase className="w-5 h-5 text-brand-400" />
                      Engenharia de Cargos (Vagas)
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
                    <p className="text-sm text-gray-400 text-center py-6">Nenhum perfil de cargo cadastrado no sistema corporativo.</p>
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

                {/* Lista de Matching de Candidatos */}
                <div className="glass-premium p-6 rounded-3xl min-h-[350px]">
                  <h3 className="text-lg font-bold text-white mb-4">Ranking de Job Matching (Similaridade de Cosseno)</h3>

                  {jobRankings.length === 0 ? (
                    <p className="text-sm text-gray-400 text-center py-10">Selecione uma vaga para exibir a compatibilidade vetorial dos candidatos.</p>
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
                              <span className="text-xs text-gray-400">Match de Cosseno</span>
                              <span className="text-xl font-black text-brand-300">{cand.matching_score}%</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

              </div>

              {/* Painel Direito: Matrix do Time (Heatmap) */}
              <div className="col-span-12 lg:col-span-5 glass-premium p-6 rounded-3xl flex flex-col justify-between min-h-[480px]">
                <div>
                  <h3 className="text-lg font-bold text-white mb-1">Team Building Matrix (Mapa de Polarizações)</h3>
                  <p className="text-xs text-gray-400 mb-4">Visualização espacial de tendências atencionais e de execução do time.</p>
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
                      Nenhum candidato mapeado na base.
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
                  Pontos vermelhos indicam profissionais com alto desvio adaptado e propensão a estresse severo.
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

      {/* ==============================================================================
          MODAL: DESENHAR VAGA (RH)
          ============================================================================== */}
      {showNewJobModal && (
        <div className="fixed inset-0 bg-black/85 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto">
          <div className="glass-premium max-w-2xl w-full p-8 rounded-3xl flex flex-col gap-6 max-h-[90vh] overflow-y-auto my-8">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-xl font-bold text-white">Desenhar Requisitos do Cargo</h3>
                <p className="text-xs text-gray-400">Configure o vetor comportamental e de motivadores ideais para a vaga.</p>
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
                  <label className="text-xs text-gray-400 font-bold block mb-1">Título do Cargo</label>
                  <input
                    type="text"
                    required
                    value={newJob.title}
                    onChange={e => setNewJob(prev => ({ ...prev, title: e.target.value }))}
                    placeholder="Ex: Engenheiro de Software Sênior"
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-brand-500"
                  />
                </div>
                <div className="col-span-2">
                  <label className="text-xs text-gray-400 font-bold block mb-1">Descrição</label>
                  <textarea
                    value={newJob.description}
                    onChange={e => setNewJob(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Descrição sumária das atribuições operacionais da vaga..."
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-brand-500 h-20"
                  />
                </div>
              </div>

              {/* Vetor DISC da Vaga */}
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
                <h4 className="text-sm font-bold text-brand-300 border-b border-white/5 pb-1 mb-3">Motivadores da Vaga (Intensidade 0-100)</h4>
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
                <h4 className="text-sm font-bold text-brand-300 border-b border-white/5 pb-1 mb-3">Preferências Junguianas da Vaga</h4>
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
