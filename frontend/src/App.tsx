import React, { useState, useEffect } from "react";
import TestRoom from "./components/TestRoom";
import Dashboards from "./components/Dashboards";
import { Brain, LogOut, ArrowRight, UserPlus, LogIn, Sparkles } from "lucide-react";

export default function App() {
  const apiBaseUrl = import.meta.env.PROD ? "/api" : "http://127.0.0.1:8000";

  // Auth States
  const [token, setToken] = useState<string | null>(localStorage.getItem("psico_token"));
  const [user, setUser] = useState<any>(JSON.parse(localStorage.getItem("psico_user") || "null"));
  
  // Modos de Visualização
  const [isRegister, setIsRegister] = useState(false);
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [registerName, setRegisterName] = useState("");
  const [registerEmail, setRegisterEmail] = useState("");
  const [registerPassword, setRegisterPassword] = useState("");
  const [registerCompany, setRegisterCompany] = useState("");
  const [authError, setAuthError] = useState<string | null>(null);

  // Status de conclusão de teste
  const [hasFinishedTest, setHasFinishedTest] = useState(false);
  const [checkingTest, setCheckingTest] = useState(false);

  // Verifica se o usuário logado concluiu os testes ao carregar a página
  useEffect(() => {
    if (token) {
      checkUserTestStatus();
    }
  }, [token]);

  const checkUserTestStatus = () => {
    setCheckingTest(true);
    fetch(`${apiBaseUrl}/results/me`, {
      headers: { "Authorization": `Bearer ${token}` }
    })
      .then(res => {
        if (res.ok) {
          setHasFinishedTest(true);
        } else {
          setHasFinishedTest(false);
        }
        setCheckingTest(false);
      })
      .catch(() => {
        setHasFinishedTest(false);
        setCheckingTest(false);
      });
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError(null);
    const formData = new URLSearchParams();
    formData.append("username", loginEmail);
    formData.append("password", loginPassword);

    try {
      const res = await fetch(`${apiBaseUrl}/auth/token`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData.toString()
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Falha ao realizar login.");
      }

      const data = await res.json();
      localStorage.setItem("psico_token", data.access_token);
      localStorage.setItem("psico_user", JSON.stringify(data.user));
      setToken(data.access_token);
      setUser(data.user);
    } catch (err: any) {
      setAuthError(err.message);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError(null);

    const payload = {
      email: registerEmail,
      password: registerPassword,
      full_name: registerName,
      company_name: registerCompany.trim() !== "" ? registerCompany : null
    };

    try {
      const res = await fetch(`${apiBaseUrl}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Erro ao realizar cadastro.");
      }

      const data = await res.json();
      localStorage.setItem("psico_token", data.access_token);
      localStorage.setItem("psico_user", JSON.stringify(data.user));
      setToken(data.access_token);
      setUser(data.user);
    } catch (err: any) {
      setAuthError(err.message);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("psico_token");
    localStorage.removeItem("psico_user");
    setToken(null);
    setUser(null);
    setHasFinishedTest(false);
  };

  // ==============================================================================
  // RENDER SE NÃO ESTIVER AUTENTICADO (TELA DE LOGIN/CADASTRO PREMIUM)
  // ==============================================================================
  if (!token || !user) {
    return (
      <div className="min-h-screen bg-[#030014] flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
        {/* Glow de fundo */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-brand-500/10 rounded-full blur-3xl pointer-events-none" />
        
        <div className="sm:mx-auto sm:w-full sm:max-w-md text-center z-10 flex flex-col items-center gap-2">
          <div className="p-3 bg-brand-500/20 rounded-2xl text-brand-400 animate-brain-wave">
            <Brain className="w-10 h-10" />
          </div>
          <h2 className="text-3xl font-extrabold text-white tracking-tight font-sans">
            Antigravity Psico
          </h2>
          <p className="text-sm text-brand-300">
            Plataforma Corporativa de Inteligência Psicométrica
          </p>
        </div>

        <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md z-10 px-4 sm:px-0">
          <div className="glass-premium py-8 px-6 sm:px-10 rounded-3xl animate-pulse-border">
            {authError && (
              <div className="mb-4 p-3.5 bg-red-900/20 border border-red-500/30 rounded-xl text-red-200 text-xs">
                {authError}
              </div>
            )}

            {isRegister ? (
              /* CADASTRO DE CANDIDATO OU RH */
              <form className="space-y-4" onSubmit={handleRegister}>
                <div>
                  <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Nome Completo</label>
                  <input
                    type="text" required
                    value={registerName}
                    onChange={e => setRegisterName(e.target.value)}
                    placeholder="Ex: João Silva"
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white focus:outline-none focus:border-brand-500 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-400 uppercase mb-1">E-mail</label>
                  <input
                    type="email" required
                    value={registerEmail}
                    onChange={e => setRegisterEmail(e.target.value)}
                    placeholder="Ex: joao@empresa.com"
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white focus:outline-none focus:border-brand-500 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Senha</label>
                  <input
                    type="password" required
                    value={registerPassword}
                    onChange={e => setRegisterPassword(e.target.value)}
                    placeholder="Mínimo 6 caracteres"
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white focus:outline-none focus:border-brand-500 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Nome da Empresa (Para RH / Opcional)</label>
                  <input
                    type="text"
                    value={registerCompany}
                    onChange={e => setRegisterCompany(e.target.value)}
                    placeholder="Ex: Antigravity Ltda (Em branco se for candidato)"
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white focus:outline-none focus:border-brand-500 text-sm"
                  />
                </div>

                <button
                  type="submit"
                  className="w-full py-3 bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 text-white font-semibold rounded-xl flex items-center justify-center gap-2 transition duration-300 shadow-md shadow-brand-500/10 text-sm"
                >
                  Criar Conta
                  <UserPlus className="w-4 h-4" />
                </button>

                <p className="text-center text-xs text-gray-400 mt-4">
                  Já possui conta?{" "}
                  <button type="button" onClick={() => { setIsRegister(false); setAuthError(null); }} className="text-brand-300 hover:underline">
                    Fazer Login
                  </button>
                </p>
              </form>
            ) : (
              /* LOGIN */
              <form className="space-y-4" onSubmit={handleLogin}>
                <div>
                  <label className="block text-xs font-bold text-gray-400 uppercase mb-1">E-mail</label>
                  <input
                    type="email" required
                    value={loginEmail}
                    onChange={e => setLoginEmail(e.target.value)}
                    placeholder="Ex: joao@empresa.com"
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white focus:outline-none focus:border-brand-500 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Senha</label>
                  <input
                    type="password" required
                    value={loginPassword}
                    onChange={e => setLoginPassword(e.target.value)}
                    placeholder="Sua senha de acesso"
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white focus:outline-none focus:border-brand-500 text-sm"
                  />
                </div>

                <button
                  type="submit"
                  className="w-full py-3 bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 text-white font-semibold rounded-xl flex items-center justify-center gap-2 transition duration-300 shadow-md shadow-brand-500/10 text-sm"
                >
                  Entrar
                  <LogIn className="w-4 h-4" />
                </button>

                <p className="text-center text-xs text-gray-400 mt-4">
                  Novo por aqui?{" "}
                  <button type="button" onClick={() => { setIsRegister(true); setAuthError(null); }} className="text-brand-300 hover:underline">
                    Criar Conta
                  </button>
                </p>
              </form>
            )}
          </div>
        </div>
      </div>
    );
  }

  // ==============================================================================
  // RENDER APP AUTENTICADO
  // ==============================================================================
  return (
    <div className="min-h-screen bg-[#030014]">
      {/* Header Corporativo Premium */}
      <header className="glass border-b border-white/5 py-4 px-6 sticky top-0 z-40">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className="w-7 h-7 text-brand-400" />
            <span className="font-extrabold text-white text-lg tracking-wider">Antigravity Psico</span>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex flex-col items-end text-xs">
              <span className="font-semibold text-white">{user.full_name}</span>
              {user.company_name ? (
                <span className="text-brand-300 text-[10px]">{user.company_name} ({user.role.toUpperCase()})</span>
              ) : (
                <span className="text-gray-400 text-[10px]">Candidato</span>
              )}
            </div>

            <button
              onClick={handleLogout}
              className="p-2.5 bg-white/5 hover:bg-red-950/20 text-gray-400 hover:text-red-400 rounded-xl border border-white/5 hover:border-red-500/20 transition"
              title="Sair"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      <main className="py-6">
        {checkingTest ? (
          <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
            <div className="w-12 h-12 border-4 border-brand-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-gray-400 text-sm">Verificando status de avaliações...</p>
          </div>
        ) : hasFinishedTest ? (
          /* Se já respondeu o teste ou se for do RH, exibe os Dashboards */
          <Dashboards token={token} apiBaseUrl={apiBaseUrl} userRole={user.role} />
        ) : (
          /* Se for candidato e não concluiu os testes, entra na sala de testes */
          <div className="py-6">
            <TestRoom 
              userId={user.id} 
              token={token} 
              apiBaseUrl={apiBaseUrl} 
              onTestComplete={() => {
                setHasFinishedTest(true);
                checkUserTestStatus();
              }} 
            />
          </div>
        )}
      </main>
    </div>
  );
}
