import React, { useState, useEffect } from "react";
import { telemetryTracker } from "../utils/telemetry";
import { draftStorage } from "../utils/indexedDB";
import { Brain, ArrowRight, Play, CheckCircle2, ShieldAlert } from "lucide-react";

interface Item {
  id: number;
  dimension: string;
  item_text: string;
}

interface Block {
  block_number: number;
  items: Item[];
}

interface TestRoomProps {
  userId: number;
  token: string;
  apiBaseUrl: string;
  onTestComplete: () => void;
}

export default function TestRoom({ userId, token, apiBaseUrl, onTestComplete }: TestRoomProps) {
  // Estados de Fluxo Geral
  const [currentTest, setCurrentTest] = useState<"BIGFIVE" | "DISC" | "SPRANGER" | "JUNG">("BIGFIVE");
  const [currentPhase, setCurrentPhase] = useState<"natural" | "adaptado">("natural");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Estados de Dados do Teste
  const [blocks, setBlocks] = useState<Block[]>([]);
  const [currentBlockIndex, setCurrentBlockIndex] = useState(0);
  const [started, setStarted] = useState(false);
  
  // Respostas locais do bloco ativo
  // DISC: { mostId: number | null, leastId: number | null }
  const [discSelection, setDiscSelection] = useState<{ most: number | null; least: number | null }>({ most: null, least: null });
  // Spranger/Jung: { itemId: rating }
  const [likertSelections, setLikertSelections] = useState<Record<number, number>>({});
  
  // Acúmulo de todas as respostas enviadas nas fases anteriores
  const [accumulatedAnswers, setAccumulatedAnswers] = useState<any[]>([]);

  // Interstício Atencional (3s Brain Calibration Pause)
  const [showPause, setShowPause] = useState(false);
  const [pauseTimer, setPauseTimer] = useState(3);
  const [pauseMessage, setPauseMessage] = useState("");

  // Busca as perguntas ao alternar de teste
  useEffect(() => {
    if (!started || showPause) return;
    
    setLoading(true);
    setError(null);
    fetch(`${apiBaseUrl}/questionnaire/items?test_type=${currentTest}`, {
      headers: { "Authorization": `Bearer ${token}` }
    })
      .then(res => {
        if (!res.ok) throw new Error("Falha ao carregar perguntas.");
        return res.json();
      })
      .then(data => {
        const preparedData = currentTest === "BIGFIVE"
          ? data.flatMap((block: Block) =>
              block.items.map((item) => ({
                block_number: block.block_number,
                items: [item]
              }))
            )
          : data;
        setBlocks(preparedData);
        setCurrentBlockIndex(0);
        
        // Tenta recuperar rascunho anterior para resiliência
        const draft = draftStorage.getDraft(userId, currentTest, currentPhase);
        if (draft) {
          setAccumulatedAnswers(draft);
          // Avança para o primeiro bloco sem resposta
          if (currentTest === "DISC") {
            const answeredBlocks = new Set(draft.map((d: any) => d.block_number));
            const firstUnanswered = preparedData.findIndex((b: Block) => !answeredBlocks.has(b.block_number));
            if (firstUnanswered !== -1) {
              setCurrentBlockIndex(firstUnanswered);
            }
          } else {
            const answeredItems = new Set(draft.map((d: any) => d.item_id));
            const firstUnanswered = preparedData.findIndex((b: Block) => !answeredItems.has(b.items[0].id));
            if (firstUnanswered !== -1) {
              setCurrentBlockIndex(firstUnanswered);
            }
          }
        } else {
          setAccumulatedAnswers([]);
        }
        
        telemetryTracker.clear();
        telemetryTracker.startBlock(preparedData[0]?.block_number || 1);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [currentTest, currentPhase, started, showPause]);

  // Temporizador da pausa de calibração cerebral
  useEffect(() => {
    let interval: any;
    if (showPause) {
      interval = setInterval(() => {
        setPauseTimer(prev => {
          if (prev <= 1) {
            setShowPause(false);
            clearInterval(interval);
            return 3;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [showPause]);

  // Função para acionar transição com micro-pausa atencional
  const triggerCerebralPause = (msg: string, nextTest: "BIGFIVE" | "DISC" | "SPRANGER" | "JUNG", nextPhase: "natural" | "adaptado") => {
    setShowPause(true);
    setPauseTimer(3);
    setPauseMessage(msg);
    setCurrentTest(nextTest);
    setCurrentPhase(nextPhase);
    setDiscSelection({ most: null, least: null });
    setLikertSelections({});
  };

  const handleStartTest = () => {
    setStarted(true);
  };

  // DISC: Grava clique telemétrico
  const handleDiscSelect = (itemId: number, type: "most" | "least") => {
    if (type === "most") {
      if (discSelection.least === itemId) return; // Não pode ser os dois ao mesmo tempo
      setDiscSelection(prev => ({ ...prev, most: itemId }));
      telemetryTracker.recordClick(itemId, 1);
    } else {
      if (discSelection.most === itemId) return;
      setDiscSelection(prev => ({ ...prev, least: itemId }));
      telemetryTracker.recordClick(itemId, -1);
    }
  };

  // Likert: Grava clique telemétrico e avança
  const handleLikertSelect = (itemId: number, score: number) => {
    setLikertSelections(prev => ({ ...prev, [itemId]: score }));
    telemetryTracker.recordClick(itemId, score);
  };

  // Botão Avançar / Submeter
  const handleNextBlock = async () => {
    const activeBlock = blocks[currentBlockIndex];
    if (!activeBlock) return;

    let newAnswers = [...accumulatedAnswers];

    if (currentTest === "DISC") {
      if (discSelection.most === null || discSelection.least === null) {
        alert("Por favor, selecione 1 adjetivo como MAIS e 1 como MENOS.");
        return;
      }
      
      // Salva dados no acumulador
      activeBlock.items.forEach(item => {
        let val = 0;
        if (item.id === discSelection.most) val = 1;
        if (item.id === discSelection.least) val = -1;
        
        // Remove anterior se houver
        newAnswers = newAnswers.filter(a => a.item_id !== item.id);
        newAnswers.push({
          item_id: item.id,
          block_number: activeBlock.block_number,
          value: val
        });
      });
      
      telemetryTracker.endBlock(activeBlock.block_number);
      setDiscSelection({ most: null, least: null });

    } else {
      // Big Five, Spranger ou Jung em escala Likert
      const item = activeBlock.items[0];
      const rating = likertSelections[item.id];
      if (rating === undefined) {
        alert("Por favor, selecione uma opção de resposta.");
        return;
      }
      
      newAnswers = newAnswers.filter(a => a.item_id !== item.id);
      newAnswers.push({
        item_id: item.id,
        block_number: activeBlock.block_number,
        value: rating
      });
      
      telemetryTracker.endBlock(activeBlock.block_number);
    }

    setAccumulatedAnswers(newAnswers);
    draftStorage.saveDraft(userId, currentTest, currentPhase, newAnswers);

    // Verifica se há mais blocos neste teste/fase
    if (currentBlockIndex < blocks.length - 1) {
      const nextIdx = currentBlockIndex + 1;
      setCurrentBlockIndex(nextIdx);
      telemetryTracker.startBlock(blocks[nextIdx].block_number);
    } else {
      // Fim do teste ativo! Submete ao Backend
      await submitCurrentPhase(newAnswers);
    }
  };

  const submitCurrentPhase = async (answersToSend: any[]) => {
    setLoading(true);
    const summary = telemetryTracker.getSummary();
    
    const payload = {
      test_type: currentTest,
      phase: currentPhase,
      answers: answersToSend,
      ttfc_avg: summary.ttfcAvg,
      irt_avg: summary.irtAvg,
      rvi_count: summary.rviCount,
      raw_telemetry: summary.raw
    };

    try {
      const res = await fetch(`${apiBaseUrl}/questionnaire/submit`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error("Falha ao salvar respostas no servidor.");
      const data = await res.json();
      
      // Limpa rascunho salvo localmente após submissão de sucesso
      draftStorage.clearDraft(userId, currentTest, currentPhase);

      // Gerencia o fluxo de transições entre testes
      if (currentTest === "DISC" && currentPhase === "natural") {
        triggerCerebralPause(
          "Perfil essencial concluído. Agora, vamos observar como seu modo de agir pode mudar em contextos do dia a dia.",
          "DISC",
          "adaptado"
        );
      } else if (currentTest === "DISC" && currentPhase === "adaptado") {
        triggerCerebralPause(
          "Fase DISC Concluída. Iniciando a avaliação dos seus Motivadores Internos (Spranger).",
          "SPRANGER",
          "natural"
        );
      } else if (currentTest === "SPRANGER") {
        triggerCerebralPause(
          "Fase de Motivadores Concluída. Iniciando a etapa final: Tipologia Cognitiva de Jung.",
          "JUNG",
          "natural"
        );
      } else if (currentTest === "BIGFIVE") {
        onTestComplete();
      } else {
        // Fim de todos os testes!
        onTestComplete();
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // ==============================================================================
  // RENDERIZAÇÃO DAS TELAS
  // ==============================================================================

  // 1. Tela de Calibração Atencional (Pause Interstice)
  if (showPause) {
    return (
      <div className="fixed inset-0 bg-[#030014] z-50 flex flex-col items-center justify-center p-6 text-center">
        <div className="absolute inset-0 bg-radial-gradient from-violet-900/10 via-transparent to-transparent pointer-events-none" />
        <div className="glass-premium max-w-lg p-10 rounded-3xl flex flex-col items-center gap-6 animate-pulse-border">
          <Brain className="w-20 h-20 text-brand-400 animate-brain-wave" />
          <h2 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-violet-300 to-indigo-200">
            Reajuste Cognitivo
          </h2>
          <p className="text-gray-400 leading-relaxed">
            {pauseMessage}
          </p>
          <div className="text-5xl font-black text-brand-400 font-mono tracking-widest mt-2 animate-bounce">
            {pauseTimer}s
          </div>
          <span className="text-xs text-gray-500 tracking-widest uppercase">
            Respire fundo. Preparando nova âncora atencional...
          </span>
        </div>
      </div>
    );
  }

  // 2. Tela de Instruções Iniciais (Welcome)
  if (!started) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16">
        <div className="glass-premium p-8 rounded-3xl flex flex-col gap-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-48 h-48 bg-brand-500/10 rounded-full blur-3xl" />
          <div className="flex items-center gap-3">
            <div className="p-3 bg-brand-500/20 rounded-2xl text-brand-400">
              <Brain className="w-8 h-8" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Avaliação Psicométrica Integrada</h1>
              <p className="text-sm text-brand-300">Big Five + camadas derivadas</p>
            </div>
          </div>

          <div className="h-[1px] bg-white/10" />

          <h3 className="text-lg font-semibold text-white">Instruções Importantes para Execução</h3>
          <ul className="space-y-4 text-gray-300 text-sm">
            <li className="flex gap-3">
              <span className="w-5 h-5 flex items-center justify-center bg-brand-500/30 text-brand-300 rounded-full text-xs font-bold shrink-0 mt-0.5">1</span>
              <span><strong>Foco Total</strong>: Reserve de 15 a 20 minutos sem interrupções. Responda em um ambiente silencioso para manter o foco cognitivo.</span>
            </li>
            <li className="flex gap-3">
              <span className="w-5 h-5 flex items-center justify-center bg-brand-500/30 text-brand-300 rounded-full text-xs font-bold shrink-0 mt-0.5">2</span>
              <span><strong>Espontaneidade</strong>: Não tente adivinhar respostas "certas". Responda como você se percebe na maior parte do tempo.</span>
            </li>
            <li className="flex gap-3">
              <span className="w-5 h-5 flex items-center justify-center bg-brand-500/30 text-brand-300 rounded-full text-xs font-bold shrink-0 mt-0.5">3</span>
              <span><strong>Conexão Segura</strong>: Se sua internet oscilar, fique calmo. O progresso é salvo localmente de forma resiliente e você retomará de onde parou.</span>
            </li>
          </ul>

          <button
            onClick={handleStartTest}
            className="mt-6 w-full py-4 bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 text-white font-semibold rounded-2xl flex items-center justify-center gap-2 transition duration-300 shadow-lg shadow-brand-500/20"
          >
            Iniciar Avaliação Psicométrica
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </div>
    );
  }

  // 3. Estado de Loading / Erros
  if (loading && blocks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
        <div className="w-12 h-12 border-4 border-brand-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-gray-400 text-sm">Carregando questionário e preparando ambiente...</p>
      </div>
    );
  }

  const activeBlock = blocks[currentBlockIndex];
  const totalBlocks = blocks.length;
  const progressPercent = totalBlocks > 0 ? Math.round(((currentBlockIndex) / totalBlocks) * 100) : 0;

  // 4. Render do Bloco de Teste
  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      {/* Barra de Progresso e Cabeçalho do Teste */}
      <div className="flex flex-col gap-3 mb-8">
        <div className="flex items-center justify-between text-xs tracking-wider text-gray-400 uppercase">
          <span>
            Teste: <strong className="text-brand-300">{currentTest}</strong> 
            {currentTest === "DISC" && ` (${currentPhase === "natural" ? "Perfil Essencial" : "Perfil Profissional"})`}
          </span>
          <span>Bloco {currentBlockIndex + 1} de {totalBlocks} ({progressPercent}%)</span>
        </div>
        <div className="w-full h-[6px] bg-white/5 rounded-full overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-brand-500 to-indigo-500 transition-all duration-500 ease-out" 
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-900/20 border border-red-500/30 rounded-2xl flex items-start gap-3 text-red-200 text-sm">
          <ShieldAlert className="w-5 h-5 shrink-0" />
          <div>
            <strong className="font-semibold block mb-0.5">Erro no Servidor</strong>
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Caixa de Instrução Focada */}
      <div className="glass p-6 rounded-2xl border-white/5 mb-6 text-sm text-gray-300 leading-relaxed">
        {currentTest === "DISC" && currentPhase === "natural" && (
          <p>👉 Responda de forma rápida e espontânea. Indique nas colunas qual adjetivo **MAIS** e qual **MENOS** descreve sua essência comportamental (natural).</p>
        )}
        {currentTest === "DISC" && currentPhase === "adaptado" && (
          <p>💼 Contexto do dia a dia: pense nas situações em que você precisa se adaptar a expectativas externas. Escolha qual adjetivo representa **MAIS** e qual **MENOS** esse modo de agir.</p>
        )}
        {currentTest === "SPRANGER" && (
          <p>🎯 Avalie a afirmação abaixo de acordo com sua prioridade de valores. Escala de 1 a 6 (1 = Discordo Totalmente, 6 = Concordo Totalmente).</p>
        )}
        {currentTest === "JUNG" && (
          <p>⚙️ Avalie o seu estilo cognitivo e preferência na afirmação abaixo de 1 a 6 (1 = Discordo Totalmente, 6 = Concordo Totalmente).</p>
        )}
        {currentTest === "BIGFIVE" && (
          <p>Avalie cada afirmação de 1 a 5 (1 = Muito imprecisa, 5 = Muito precisa).</p>
        )}
      </div>

      {/* Bloco de Questões */}
      {activeBlock && (
        <div className="glass-premium p-8 rounded-3xl flex flex-col gap-6 min-h-[300px]">
          {currentTest === "DISC" ? (
            /* Render de Escolha Forçada DISC */
            <div className="flex flex-col gap-4">
              {/* Cabeçalho da Tabela */}
              <div className="grid grid-cols-12 text-center text-xs font-semibold text-gray-400 tracking-wider pb-2 border-b border-white/5">
                <div className="col-span-6 text-left">Adjetivo</div>
                <div className="col-span-3">Mais (+1)</div>
                <div className="col-span-3">Menos (-1)</div>
              </div>

              {/* Itens do Bloco */}
              <div className="divide-y divide-white/5">
                {activeBlock.items.map((item) => (
                  <div key={item.id} className="grid grid-cols-12 text-center py-4 items-center transition hover:bg-white/[0.01]">
                    <div className="col-span-6 text-left font-medium text-white text-base">{item.item_text}</div>
                    
                    {/* Botão MAIS */}
                    <div className="col-span-3 flex justify-center">
                      <button
                        onClick={() => handleDiscSelect(item.id, "most")}
                        className={`w-6 h-6 rounded-full border flex items-center justify-center transition ${
                          discSelection.most === item.id 
                            ? "bg-brand-500 border-brand-400 shadow-md shadow-brand-500/50" 
                            : "border-white/20 hover:border-white/40"
                        }`}
                      >
                        {discSelection.most === item.id && <div className="w-2.5 h-2.5 bg-white rounded-full" />}
                      </button>
                    </div>

                    {/* Botão MENOS */}
                    <div className="col-span-3 flex justify-center">
                      <button
                        onClick={() => handleDiscSelect(item.id, "least")}
                        className={`w-6 h-6 rounded-full border flex items-center justify-center transition ${
                          discSelection.least === item.id 
                            ? "bg-indigo-600 border-indigo-400 shadow-md shadow-indigo-500/50" 
                            : "border-white/20 hover:border-white/40"
                        }`}
                      >
                        {discSelection.least === item.id && <div className="w-2.5 h-2.5 bg-white rounded-full" />}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            /* Render de Escala Likert */
            <div className="flex flex-col items-center justify-center gap-8 py-4">
              <h2 className="text-xl font-medium text-white text-center leading-relaxed px-4">
                "{activeBlock.items[0]?.item_text}"
              </h2>

              {/* Círculos da Escala Likert */}
              <div className="flex items-center gap-2 sm:gap-4 mt-4">
                <span className="text-xs text-red-400 uppercase font-semibold tracking-wider mr-2 hidden sm:block">
                  {currentTest === "BIGFIVE" ? "Imprecisa" : "Discordo"}
                </span>
                {(currentTest === "BIGFIVE" ? [1, 2, 3, 4, 5] : [1, 2, 3, 4, 5, 6]).map((score) => {
                  const itemId = activeBlock.items[0]?.id;
                  const isSelected = likertSelections[itemId] === score;
                  return (
                    <button
                      key={score}
                      onClick={() => handleLikertSelect(itemId, score)}
                      className={`w-10 h-10 sm:w-12 sm:h-12 rounded-full border-2 flex items-center justify-center font-bold text-lg transition duration-300 ${
                        isSelected 
                          ? "bg-gradient-to-tr from-brand-600 to-indigo-600 border-brand-400 text-white shadow-lg shadow-brand-500/30 scale-110" 
                          : "border-white/10 hover:border-white/30 text-gray-400 hover:text-white"
                      }`}
                    >
                      {score}
                    </button>
                  );
                })}
                <span className="text-xs text-brand-300 uppercase font-semibold tracking-wider ml-2 hidden sm:block">
                  {currentTest === "BIGFIVE" ? "Precisa" : "Concordo"}
                </span>
              </div>
              <div className="flex justify-between w-full px-8 sm:hidden text-[10px] text-gray-400 uppercase tracking-widest font-semibold mt-2">
                <span>{currentTest === "BIGFIVE" ? "Imprecisa" : "Discordo"}</span>
                <span>{currentTest === "BIGFIVE" ? "Precisa" : "Concordo"}</span>
              </div>
            </div>
          )}

          <div className="h-[1px] bg-white/5 mt-4" />

          {/* Botão de Navegação do Bloco */}
          <div className="flex justify-end">
            <button
              onClick={handleNextBlock}
              disabled={loading}
              className="px-8 py-3.5 bg-white text-[#030014] font-semibold rounded-xl flex items-center gap-2 hover:bg-gray-200 transition disabled:opacity-50"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-[#030014] border-t-transparent rounded-full animate-spin" />
              ) : currentBlockIndex === totalBlocks - 1 ? (
                <>
                  Submeter Etapa
                  <CheckCircle2 className="w-5 h-5" />
                </>
              ) : (
                <>
                  Próximo Bloco
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
