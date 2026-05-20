// Resiliência Anti-Drop: Permite salvar as respostas parciais para que o usuário não as perca caso feche o navegador ou oscile a conexão.
const STORAGE_PREFIX = "psico_draft_";

export const draftStorage = {
  saveDraft(userId: number, testType: string, phase: string, answers: any[]) {
    try {
      const key = `${STORAGE_PREFIX}${userId}_${testType}_${phase}`;
      localStorage.setItem(key, JSON.stringify({
        answers,
        timestamp: Date.now()
      }));
    } catch (e) {
      console.error("Erro ao salvar rascunho de respostas localmente:", e);
    }
  },

  getDraft(userId: number, testType: string, phase: string): any[] | null {
    try {
      const key = `${STORAGE_PREFIX}${userId}_${testType}_${phase}`;
      const data = localStorage.getItem(key);
      if (!data) return null;
      const parsed = JSON.parse(data);
      
      // Expira rascunhos com mais de 24 horas
      if (Date.now() - parsed.timestamp > 24 * 60 * 60 * 1000) {
        localStorage.removeItem(key);
        return null;
      }
      return parsed.answers;
    } catch (e) {
      console.error("Erro ao recuperar rascunho:", e);
      return null;
    }
  },

  clearDraft(userId: number, testType: string, phase: string) {
    try {
      const key = `${STORAGE_PREFIX}${userId}_${testType}_${phase}`;
      localStorage.removeItem(key);
    } catch (e) {
      console.error("Erro ao limpar rascunho:", e);
    }
  }
};
