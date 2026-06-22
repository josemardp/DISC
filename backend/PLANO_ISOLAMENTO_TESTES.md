# Plano de Isolamento de Testes

**Data:** 2026-06-22  
**Escopo:** backend/app/ — 38 testes, SQLite :memory:, FastAPI + SQLAlchemy  
**Objetivo:** tornar a suíte determinística e independente de ordem, SEM alterar lógica de produção.

---

## 1. Diagnóstico do estado atual

### 1.1 Estrutura da fixture atual

`conftest.py` tem uma única fixture `scope="session"`, `autouse=True`:

```python
@pytest.fixture(scope="session", autouse=True)
def create_tables_and_seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_db(db)
    db.close()
```

Problema: cria schema e insere dados de seed **uma única vez**, sem nenhum teardown entre testes.
Todos os testes compartilham o mesmo banco acumulado.

### 1.2 Por que o banco acumula

`database.py` configura o engine com `StaticPool` para `sqlite:///:memory:`:

```python
engine = create_engine(
    db_url,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
```

`StaticPool` faz com que **todos** os `SessionLocal()` e `engine.connect()` reusem a
**mesma conexão física** com o SQLite. Isso é necessário para que o banco `:memory:` não
desapareça a cada nova conexão — mas como efeito colateral, cada teste deixa linhas
acumuladas visíveis para os próximos.

### 1.3 Sintomas concretos dos 38 testes

| Teste | Problema de estado |
|---|---|
| `test_reliability_source_default_com_poucos_respondentes` | Conta `PsychometricResult.respondent_id` distintos globalmente. Passa hoje por acidente (N < 30). Viraria se a suíte acumulasse ≥ 30 usuários. |
| `test_delete_consolidado_preserva_bigfive` | Insere `PsychometricResult(respondent_id=999999)` sem criar User (FK não imposta pelo SQLite). Tem limpeza manual em `finally` — gambiarra compensatória. |
| Todos os testes com `TestClient` | Cada `with TestClient(app) as client:` aciona o `lifespan`, que chama `seed_db`. Como `seed_db` é idempotente, não duplica itens — mas todos os Users e PsychometricResults de testes anteriores continuam no banco. |

---

## 2. Por que "rollback de transação" NÃO funciona aqui

A estratégia clássica de rollback por teste consiste em:
1. Abrir uma transação no início do teste.
2. Fazer todas as operações nela.
3. Dar rollback no teardown (sem commit).

**Ela não funciona neste contexto por duas razões:**

**Razão A — os route handlers chamam `db.commit()`.**  
Todas as rotas FastAPI terminam com `db.commit()`. O `db.commit()` em SQLAlchemy chama
`connection.commit()` na conexão subjacente. Com `StaticPool`, há **uma única conexão
física**; chamar `.commit()` nela fecha a transação e persiste os dados permanentemente.
Nenhum rollback posterior pode desfazê-los.

**Razão B — SQLite tem suporte limitado a transações aninhadas (savepoints).**  
Mesmo usando a técnica de "session bound to connection" com savepoints externos, o
SQLite não garante rollback completo se alguma operação fez `COMMIT` explícito — que é
exatamente o que os handlers fazem.

**Conclusão:** rollback de transação por teste é inviável aqui.

---

## 3. Por que "drop/recreate por teste" é desnecessário

Recriar schema a cada teste (via `Base.metadata.drop_all` + `create_all` + `seed_db`)
funcionaria, mas tem dois custos desnecessários:

1. **Velocidade:** drop/create de 8 tabelas + ~200 linhas de seed × 38 testes ≈
   overhead relevante, principalmente se a suíte crescer.
2. **Fragilidade de metadata:** exige que todos os models estejam importados antes de
   `drop_all`. Com lazy imports, tabelas podem não ser registradas em `Base.metadata`.

O problema real **não é o schema** (que é imutável durante a suíte) — é o **dado
acumulado** por testes. A solução certa apaga apenas os dados.

---

## 4. Estratégia recomendada: truncação por função (fixture autouse function-scoped)

### 4.1 Mecanismo

Adicionar ao `conftest.py` uma **segunda fixture**, `scope="function"`, `autouse=True`,
que **após cada teste** apaga todas as linhas de dados transacionais, deixando apenas os
dados de seed intocados (QuestionnaireItems, seed Users, seed Tenant).

```
Estrutura resultante do conftest.py:

  [session] create_tables_and_seed   — cria schema + seed, 1 vez só
  [function] clean_transactional_data — DELETE nas tabelas de dados após cada teste
```

### 4.2 Ordem de deleção (respeito às FKs)

Mesmo que o SQLite não imponha FKs por padrão, a ordem correta é da tabela mais
dependente para a menos dependente:

```
1. personal_reflections   → FK para users e psychometric_results
2. reports                → FK para users e psychometric_results
3. psychometric_results   → FK para users
4. telemetry_sessions     → FK para users
5. responses              → FK para users e questionnaire_items
6. jobs                   → FK para tenants
7. users (não-seed)       → FK para tenants (nullable)
```

`questionnaire_items`, `tenants` e os 3 seed users **não** são tocados.

### 4.3 Identificação dos dados de seed

Os seed Users são identificados pelos e-mails fixos em `seed.py`:
```
admin@empresa.com, candidato@empresa.com, super@sistema.com
```

Na fixture de limpeza:
```python
_SEED_EMAILS = frozenset({"admin@empresa.com", "candidato@empresa.com", "super@sistema.com"})
db.query(User).filter(~User.email.in_(_SEED_EMAILS)).delete(synchronize_session=False)
```

### 4.4 Interação com lifespan / seed

Cada `with TestClient(app) as client:` aciona o `lifespan`, que chama `seed_db`.
`seed_db` é idempotente (verifica existência antes de inserir). Após a limpeza de
um teste, na entrada do próximo `TestClient`:

- `QuestionnaireItem` count > 0 → seed pula os itens ✓
- Seed users existem → seed pula os users ✓
- Seed tenant existe → seed pula o tenant ✓

Nenhum re-seeding desnecessário. Nenhuma colisão.

### 4.5 Interação com testes que usam `SessionLocal()` diretamente

Testes como `test_delete_consolidado_preserva_bigfive` criam sessões diretamente
(não via `TestClient`). Essas sessões usam a mesma `StaticPool` e, portanto, o mesmo
banco. A fixture de limpeza também usa `SessionLocal()` — vê exatamente os mesmos dados.
Não há discrepância.

### 4.6 Efeito no `test_delete_consolidado_preserva_bigfive`

Com isolamento:
- O banco começa limpo (apenas dados de seed).
- O teste insere 2 `PsychometricResult` para `respondent_id=999999` (sem criar User —
  funciona porque SQLite não impõe FK por padrão).
- O teste faz a asserção.
- A fixture de limpeza apaga esses resultados no teardown.
- **O bloco `finally` de limpeza manual dentro do teste se torna desnecessário**
  e deve ser removido (é exatamente o que o isolamento substitui).

A semântica do teste (o que ele afirma) não muda; apenas a limpeza sai do corpo do
teste para o fixture.

### 4.7 Efeito nos testes `test_reliability_source_*`

Com isolamento, cada um desses testes começa com **zero** `PsychometricResult`. O teste
registra 1 usuário e submete 1 aplicação → `n_respondentes = 1`. O resultado
`reliability_source = "default_literatura"` é **garantido por construção** (1 < 30),
não por acidente (banco vazio por ser o primeiro teste). Nenhuma alteração semântica
necessária nesses testes.

---

## 5. Testes que precisarão de ajuste

| Teste | Ajuste necessário | Motivo |
|---|---|---|
| `test_delete_consolidado_preserva_bigfive` | Remover bloco `finally` com limpeza manual de `user_id=999999` | O fixture de teardown trata isso; a limpeza manual é gambiarra de banco sem isolamento |
| `test_reliability_source_default_com_poucos_respondentes` | Nenhum | Com banco limpo por fixture, N=1 é garantido; asserção permanece idêntica |
| `test_reliability_source_existe_na_resposta` | Nenhum | Idem |
| Todos os outros | Nenhum | Funcionam com banco limpo; `seed_db` re-idempotente via lifespan |

---

## 6. Impacto em `database.py` (lógica de produção)

**Zero.** A estratégia resolve tudo na camada de teste (`conftest.py` + ajuste em
`test_main.py`). `database.py`, `main.py`, `science_engine.py`, `models.py` e todos
os demais arquivos de produção permanecem intocados.

---

## 7. pytest-randomly (solicitação de aprovação)

Para **provar** independência de ordem de forma reproduzível e automatizável, recomendo
adicionar `pytest-randomly` como dependência de desenvolvimento.

**Justificativa:**
- pytest não tem flag nativa de "ordem aleatória reproduzível".
- `pytest-randomly` embaralha os testes com uma semente (`--randomly-seed=N`) que pode
  ser fixada em CI para reproduzir falhas.
- Sem ele, posso demonstrar ordem invertida rodando os testes em dois subconjuntos
  ou manualmente, mas a prova é frágil.

**Uso proposto:**
```bash
# ordem padrão
python -m pytest backend/app/ -v

# ordem aleatória (semente aleatória impressa no cabeçalho)
python -m pytest backend/app/ -v -p randomly

# mesma semente para reproduzir
python -m pytest backend/app/ -v -p randomly --randomly-seed=<N>
```

**Impacto em produção:** zero — é dependência só de teste, não vai para o runtime.  
**Instalação:** `pip install pytest-randomly` (não altera requirements.txt de produção;
pode ir em `requirements-dev.txt` se o projeto tiver, ou declarado apenas aqui).

**Solicito aprovação para instalar `pytest-randomly` e usá-lo na prova de ordem.**  
Se não aprovado, demonstrarei ordem independente com duas execuções manuais em ordens
distintas (ex.: todos os testes de `test_science_engine.py` antes de `test_main.py`,
e vice-versa).

---

## 8. Resumo do que muda

| Arquivo | O que muda |
|---|---|
| `backend/app/conftest.py` | Renomear fixture existente; adicionar fixture `function`-scoped de limpeza |
| `backend/app/test_main.py` | Remover bloco `finally` de limpeza manual em `test_delete_consolidado_preserva_bigfive` |
| Todos os outros arquivos | **Nenhuma alteração** |

---

## 9. Critério de aceite

- `python -m pytest backend/app/ -v` → 38 verdes (ou 38 + novo teste de isolamento se aprovado).
- Duas execuções em ordens distintas → ambas 100% verdes.
- `test_reliability_source_default_com_poucos_respondentes` garante `N < 30` por
  construção, não por acidente.
- `test_delete_consolidado_preserva_bigfive` sem limpeza manual no corpo do teste.
