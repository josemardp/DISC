from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
import csv
import hashlib
import io
import json
import os
import secrets
import traceback as _traceback
from jose import JWTError, jwt


from backend.app.config import settings
from backend.app.database import engine, Base, get_db
from backend.app.models import Tenant, User, QuestionnaireItem, Response, TelemetrySession, PsychometricResult, PersonalReflection, Report, Job
from backend.app.math_engine import (
    raw_to_percentile, calculate_euclidean_distance, calculate_cosine_similarity,
    detect_frictions
)
from backend.app.science_engine import (
    score_big_five, percentil_intraindividual,
    derive_jung_from_big_five,
    derive_disc_from_big_five, derive_spranger_from_big_five,
    mcdonald_omega, standard_error_of_measurement, confidence_interval,
    response_quality_index
)
from backend.app.seed_big_five_ipip import ITENS_ATENCAO
from backend.app.gemini_service import generate_psychometric_report

ALLOWED_TEST_TYPES = {"BIGFIVE", "DISC", "SPRANGER", "JUNG"}
ALLOWED_PHASES_BY_TEST = {
    "BIGFIVE": {"natural"},
    "DISC": {"natural", "adaptado"},
    "SPRANGER": {"natural"},
    "JUNG": {"natural"},
}
VALUE_RANGES_BY_TEST = {
    "BIGFIVE": (1, 5),
    "DISC": (-1, 1),
    "SPRANGER": (1, 6),
    "JUNG": (1, 6),
}
NON_DIAGNOSTIC_NOTICE = (
    "Este resultado é uma ferramenta de autoconhecimento e não constitui diagnóstico "
    "psicológico, laudo psicológico ou avaliação psicológica profissional."
)


def _is_production() -> bool:
    return settings.ENV == "production"


def _cors_origins() -> List[str]:
    if _is_production():
        return [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]
    configured = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]
    return configured or ["*"]


@asynccontextmanager
async def lifespan(app):
    try:
        if not _is_production() and settings.AUTO_CREATE_SCHEMA:
            Base.metadata.create_all(bind=engine)
            if settings.ENABLE_DEMO_SEED or settings.ENV in {"development", "test"}:
                from backend.app.seed import seed_db
                db = next(get_db())
                try:
                    seed_db(db)
                finally:
                    db.close()
    except Exception as e:
        import traceback
        print(f"[startup] erro não-fatal: {e}", flush=True)
        traceback.print_exc()
    yield


# Inicialização da API
app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0", lifespan=lifespan)

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    tb = _traceback.format_exc()
    print(f"[error] {type(exc).__name__}: {exc}", flush=True)
    print(tb, flush=True)
    if _is_production():
        return JSONResponse(
            status_code=500,
            content={"detail": "Erro interno. A equipe técnica foi notificada."}
        )
    return JSONResponse(
        status_code=500,
        content={"detail": f"{type(exc).__name__}: {str(exc)[:300]}"}
    )

# Middleware para normalizar caminhos na Vercel (remove /api se presente)
@app.middleware("http")
async def strip_api_prefix(request, call_next):
    forwarded_path = request.headers.get("x-vercel-forwarded-path") or request.headers.get("x-matched-path")
    if forwarded_path:
        path = forwarded_path
    else:
        path = request.scope.get("path", "")
        
    print(f"DEBUG MIDDLEWARE: Original path = {request.scope.get('path', '')}, Forwarded = {forwarded_path}")
    
    if path.startswith("/api"):
        path = path[4:]
        
    if not path.startswith("/"):
        path = "/" + path
        
    request.scope["path"] = path
    print(f"DEBUG MIDDLEWARE: Final path = {request.scope.get('path', '')}")
    return await call_next(request)

# Configuração de CORS para permitir requisições do frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials="*" not in _cors_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return f"pbkdf2_sha256$100000${salt}${dk.hex()}"

def verify_password(password: str, hashed: str) -> bool:
    try:
        if hashed.startswith("pbkdf2_sha256$"):
            parts = hashed.split("$")
            iterations = int(parts[1])
            salt = parts[2]
            original_hash = parts[3]
            dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations)
            return dk.hex() == original_hash
        return False
    except Exception:
        return False

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais de acesso.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# Pydantic Schemas
class UserRegister(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str
    full_name: str
    company_name: Optional[str] = None  # Se preenchido, cria tenant ou vincula

class Token(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]

class AnswerItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_id: int
    block_number: int
    value: int  # DISC: +1 (Mais), -1 (Menos). Likert: 1-6.

class ReflectionSubmission(BaseModel):
    model_config = ConfigDict(extra="forbid")

    self_understanding_goal: Optional[str] = Field(default=None, max_length=1000)
    current_pattern_to_observe: Optional[str] = Field(default=None, max_length=1000)

class TestSubmission(BaseModel):
    model_config = ConfigDict(extra="forbid")

    test_type: str  # DISC, SPRANGER, JUNG
    phase: str  # natural, adaptado
    answers: List[AnswerItem]
    # Telemetria
    ttfc_avg: float
    irt_avg: float
    rvi_count: int
    raw_telemetry: Optional[List[Dict[str, Any]]] = None
    reflections: Optional[ReflectionSubmission] = None

class JobCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: Optional[str] = ""
    target_d: float
    target_i: float
    target_s: float
    target_c: float
    target_spranger: Dict[str, float]
    target_jung: Dict[str, float]

# ==============================================================================
# ROTAS DE AUTENTICAÇÃO
# ==============================================================================

@app.post("/auth/register", response_model=Token)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user_in.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")
    
    tenant_id = None
    if user_in.company_name:
        tenant = db.query(Tenant).filter(Tenant.name == user_in.company_name).first()
        if not tenant:
            tenant = Tenant(name=user_in.company_name)
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
        tenant_id = tenant.id
        
    hashed_pwd = hash_password(user_in.password)
    new_user = User(
        email=user_in.email,
        hashed_password=hashed_pwd,
        full_name=user_in.full_name,
        role="respondent",
        tenant_id=tenant_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": new_user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "role": new_user.role,
            "company_name": user_in.company_name,
            "hr_request_status": "requires_admin_approval" if user_in.company_name else None
        }
    }

@app.post("/auth/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="E-mail ou senha incorretos.")
    
    company_name = None
    if user.tenant_id:
        tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
        if tenant:
            company_name = tenant.name
            
    access_token = create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "company_name": company_name
        }
    }

# ==============================================================================
# ROTAS DO QUESTIONÁRIO
# ==============================================================================

@app.get("/questionnaire/items")
def get_items(test_type: str, db: Session = Depends(get_db)):
    """
    Retorna os itens do questionário filtrados pelo tipo de teste (DISC, SPRANGER, JUNG).
    Garante o agrupamento por bloco no frontend.
    """
    items = db.query(QuestionnaireItem).filter(QuestionnaireItem.test_type == test_type).order_by(
        QuestionnaireItem.block_number, QuestionnaireItem.id
    ).all()
    
    # Agrupa por bloco para facilitar a renderização
    blocks = {}
    for item in items:
        b_num = item.block_number
        if b_num not in blocks:
            blocks[b_num] = []
        blocks[b_num].append({
            "id": item.id,
            "dimension": item.dimension,
            "item_text": item.item_text,
            "weight": item.weight,
            "reverse_keyed": item.reverse_keyed
        })
        
    return [{"block_number": k, "items": v} for k, v in sorted(blocks.items())]


def _validate_submission_payload(submission: TestSubmission, db: Session) -> List[QuestionnaireItem]:
    test_type = submission.test_type.upper()
    phase = submission.phase.lower()
    if test_type not in ALLOWED_TEST_TYPES:
        raise HTTPException(status_code=422, detail="test_type inválido.")
    if phase not in ALLOWED_PHASES_BY_TEST[test_type]:
        raise HTTPException(status_code=422, detail="phase inválida para o test_type informado.")
    if not submission.answers:
        raise HTTPException(status_code=422, detail="answers não pode estar vazio.")

    submitted_ids = [answer.item_id for answer in submission.answers]
    if len(submitted_ids) != len(set(submitted_ids)):
        raise HTTPException(status_code=422, detail="Payload contém item duplicado.")

    expected_items = db.query(QuestionnaireItem).filter(
        QuestionnaireItem.test_type == test_type
    ).all()
    expected_by_id = {item.id: item for item in expected_items}
    submitted_set = set(submitted_ids)
    expected_set = set(expected_by_id.keys())

    unknown = sorted(submitted_set - expected_set)
    if unknown:
        raise HTTPException(status_code=422, detail=f"Payload contém item_id desconhecido: {unknown[:5]}.")

    missing = sorted(expected_set - submitted_set)
    if missing:
        raise HTTPException(status_code=422, detail=f"Payload incompleto: {len(missing)} item(ns) ausente(s).")

    min_value, max_value = VALUE_RANGES_BY_TEST[test_type]
    for answer in submission.answers:
        item = expected_by_id[answer.item_id]
        if answer.block_number != item.block_number:
            raise HTTPException(status_code=422, detail=f"block_number incompatível para item_id {answer.item_id}.")
        if not (min_value <= answer.value <= max_value):
            raise HTTPException(status_code=422, detail=f"value fora da escala permitida para {test_type}.")
        if test_type == "DISC" and answer.value not in {-1, 0, 1}:
            raise HTTPException(status_code=422, detail="value inválido para DISC.")

    return [expected_by_id[item_id] for item_id in submitted_ids]

@app.post("/questionnaire/submit")
def submit_responses(submission: TestSubmission, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    submission.test_type = submission.test_type.upper()
    submission.phase = submission.phase.lower()
    _validate_submission_payload(submission, db)
    if submission.reflections is not None and submission.test_type != "BIGFIVE":
        raise HTTPException(status_code=422, detail="Reflexões pessoais só podem acompanhar uma aplicação Big Five.")
    # 1. Apaga respostas anteriores do mesmo teste/fase para evitar duplicados
    db.query(Response).filter(
        Response.respondent_id == current_user.id,
        Response.test_type == submission.test_type,
        Response.phase == submission.phase
    ).delete()
    
    # 2. Ingestão de Respostas
    for ans in submission.answers:
        resp = Response(
            respondent_id=current_user.id,
            item_id=ans.item_id,
            block_number=ans.block_number,
            test_type=submission.test_type,
            phase=submission.phase,
            value=ans.value
        )
        db.add(resp)

    # 3. Ingestão de Telemetria e análise de fraude
    is_fraud = False
    reasons = []
    
    # Se latência média for menor que 800ms
    if submission.irt_avg < 800:
        is_fraud = True
        reasons.append("LinearResponsePattern: Velocidade de clique excessiva (< 800ms por item).")
        
    # Detecção de Social Desirability em adjetivos/perguntas sensíveis
    # Se mudou de ideia muitas vezes (RVI alto > 10) em termos comportamentais estruturados
    if submission.rvi_count > 10:
        reasons.append("HighVolatilityPattern: Alteração excessiva de escolhas (Social Desirability).")

    db.query(TelemetrySession).filter(
        TelemetrySession.respondent_id == current_user.id,
        TelemetrySession.test_type == submission.test_type,
        TelemetrySession.phase == submission.phase
    ).delete()

    telemetry = TelemetrySession(
        respondent_id=current_user.id,
        test_type=submission.test_type,
        phase=submission.phase,
        ttfc_avg=submission.ttfc_avg,
        irt_avg=submission.irt_avg,
        rvi_count=submission.rvi_count,
        is_fraud_suspect=is_fraud,
        fraud_reasons=reasons,
        raw_telemetry=submission.raw_telemetry
    )
    db.add(telemetry)
    db.commit()

    if submission.test_type == "BIGFIVE":
        result = process_psychometric_results(current_user.id, db)
        if submission.reflections is not None:
            self_goal = (submission.reflections.self_understanding_goal or "").strip() or None
            pattern = (submission.reflections.current_pattern_to_observe or "").strip() or None
            if self_goal or pattern:
                db.add(PersonalReflection(
                    respondent_id=current_user.id,
                    result_id=result.id,
                    self_understanding_goal=self_goal,
                    current_pattern_to_observe=pattern
                ))
                db.commit()
        return {"status": "success", "all_completed": True}

    # 4. Verifica se completou TODOS os testes requeridos para processar o perfil consolidado
    # Requisitos: DISC natural, DISC adaptado, Spranger natural (fase única), Jung natural (fase única)
    completed_tests = db.query(Response.test_type, Response.phase).filter(
        Response.respondent_id == current_user.id
    ).distinct().all()
    
    test_matrix = {("DISC", "natural"), ("DISC", "adaptado"), ("SPRANGER", "natural"), ("JUNG", "natural")}
    has_completed_all = test_matrix.issubset(set(completed_tests))

    if has_completed_all:
        process_psychometric_results(current_user.id, db)

    return {"status": "success", "all_completed": has_completed_all}

# ==============================================================================
# MOTOR DE PROCESSAMENTO DE PERFIL
# ==============================================================================

def load_norm_source(source_name: str) -> dict:
    json_path = os.path.join(os.path.dirname(__file__), "norms_ipip_neo.json")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    sources = data.get("sources", {})
    if source_name not in sources:
        raise ValueError(
            f"Fonte de normas '{source_name}' não encontrada em norms_ipip_neo.json. "
            f"Fontes disponíveis: {list(sources.keys())}"
        )
    return sources[source_name]


def _attention_expected_by_item_id(db: Session) -> Dict[int, int]:
    attention_items = db.query(QuestionnaireItem).filter(
        QuestionnaireItem.test_type == "BIGFIVE",
        QuestionnaireItem.dimension == "attention_check"
    ).order_by(QuestionnaireItem.id).all()
    return {
        item.id: ITENS_ATENCAO[idx]["expected"]
        for idx, item in enumerate(attention_items)
        if idx < len(ITENS_ATENCAO)
    }


def _bigfive_raw_history(user_id: int, db: Session) -> Dict[str, List[float]]:
    previous_results = db.query(PsychometricResult).filter(
        PsychometricResult.respondent_id == user_id,
        PsychometricResult.bigfive_percentis.isnot(None)
    ).order_by(PsychometricResult.created_at.asc()).all()
    return {
        "O": [r.bigfive_O for r in previous_results],
        "C": [r.bigfive_C for r in previous_results],
        "E": [r.bigfive_E for r in previous_results],
        "A": [r.bigfive_A for r in previous_results],
        "N": [r.bigfive_N for r in previous_results],
    }


def _bigfive_norm_label() -> str:
    if settings.NORM_MODE == "intra":
        return "régua interna — não é percentil populacional"
    if settings.NORM_MODE == "public":
        return f"norma pública: {settings.NORM_SOURCE}"
    return "modo de norma desconhecido"


def _bigfive_history_entries(user_id: int, db: Session) -> List[Dict[str, Any]]:
    results = db.query(PsychometricResult).filter(
        PsychometricResult.respondent_id == user_id,
        PsychometricResult.bigfive_percentis.isnot(None)
    ).order_by(PsychometricResult.created_at.asc()).all()

    entries = []
    for idx, row in enumerate(results):
        percentiles = row.bigfive_percentis or {}
        is_baseline = settings.NORM_MODE == "intra" and all(
            percentiles.get(factor) is None for factor in ["O", "C", "E", "A", "N"]
        )
        entries.append({
            "id": row.id,
            "created_at": row.created_at,
            "sequence": idx + 1,
            "bigfive_raw": {
                "O": row.bigfive_O,
                "C": row.bigfive_C,
                "E": row.bigfive_E,
                "A": row.bigfive_A,
                "N": row.bigfive_N
            },
            "bigfive_percentiles": percentiles,
            "quality_label": row.quality_label,
            "norm_label": "linha de base interna" if is_baseline else _bigfive_norm_label()
        })
    return entries


def _bigfive_scaled_scores(raw_scores: Dict[str, float], history: Dict[str, List[float]]) -> Dict[str, float]:
    if settings.NORM_MODE == "intra":
        if not any(history.get(factor) for factor in ["O", "C", "E", "A", "N"]):
            return {factor: None for factor in ["O", "C", "E", "A", "N"]}
        return {
            factor: percentil_intraindividual(raw_scores[factor], history.get(factor, []))["posicao_relativa"]
            for factor in ["O", "C", "E", "A", "N"]
        }
    if settings.NORM_MODE == "public":
        try:
            norm = load_norm_source(settings.NORM_SOURCE)
        except (FileNotFoundError, ValueError) as exc:
            raise HTTPException(status_code=500, detail=f"Norma pública indisponível: {exc}") from exc
        return {
            factor: raw_to_percentile(raw_scores[factor], norm[factor]["mean"], norm[factor]["sd"])
            for factor in ["O", "C", "E", "A", "N"]
        }
    raise HTTPException(
        status_code=500,
        detail=f"NORM_MODE='{settings.NORM_MODE}' inválido. Use 'intra' ou 'public'."
    )


def _process_bigfive_results(user_id: int, db: Session):
    rows = db.query(Response, QuestionnaireItem).join(
        QuestionnaireItem, Response.item_id == QuestionnaireItem.id
    ).filter(
        Response.respondent_id == user_id,
        Response.test_type == "BIGFIVE"
    ).all()

    scored_inputs = []
    attention_responses = []
    for resp, item in rows:
        if item.dimension == "attention_check":
            attention_responses.append(resp)
            continue
        scored_inputs.append({
            "dimension": item.dimension,
            "value": resp.value,
            "reverse_keyed": item.reverse_keyed
        })

    scores = score_big_five(scored_inputs)
    raw_scores = {factor: scores[factor]["raw"] for factor in ["O", "C", "E", "A", "N"]}
    history = _bigfive_raw_history(user_id, db)
    scaled_scores = _bigfive_scaled_scores(raw_scores, history)
    jung_continuo = derive_jung_from_big_five(scaled_scores)
    disc_derivado = derive_disc_from_big_five(scaled_scores)
    spranger_derivado = derive_spranger_from_big_five(scaled_scores)

    expected = _attention_expected_by_item_id(db)
    atencao_ok = all(resp.value == expected.get(resp.item_id) for resp in attention_responses)
    if not attention_responses:
        atencao_ok = False

    telemetry = db.query(TelemetrySession).filter(
        TelemetrySession.respondent_id == user_id,
        TelemetrySession.test_type == "BIGFIVE"
    ).order_by(TelemetrySession.created_at.desc()).first()

    quality = response_quality_index(
        valores=[int(r["value"]) for r in scored_inputs],
        atencao_ok=atencao_ok,
        irt_avg_ms=telemetry.irt_avg if telemetry else 0,
        rvi_count=telemetry.rvi_count if telemetry else 0
    )

    result = PsychometricResult(
        respondent_id=user_id,
        bigfive_O=raw_scores["O"],
        bigfive_C=raw_scores["C"],
        bigfive_E=raw_scores["E"],
        bigfive_A=raw_scores["A"],
        bigfive_N=raw_scores["N"],
        bigfive_percentis=scaled_scores,
        jung_continuo=jung_continuo,
        quality_label=quality["quality_label"],
        natural_percentile_d=disc_derivado["D"],
        natural_percentile_i=disc_derivado["I"],
        natural_percentile_s=disc_derivado["S"],
        natural_percentile_c=disc_derivado["C"],
        spranger_percentile_teorico=spranger_derivado["teorico"],
        spranger_percentile_economico=spranger_derivado["economico"],
        spranger_percentile_estetico=spranger_derivado["estetico"],
        spranger_percentile_social=spranger_derivado["social"],
        spranger_percentile_individualista=spranger_derivado["individualista"],
        spranger_percentile_regulador=spranger_derivado["regulador"],
        jung_dominant_type=jung_continuo["tipo_resumo"],
        jung_scores=jung_continuo["eixos"],
        frictions=[]
    )
    db.add(result)
    db.commit()
    return result

def process_psychometric_results(user_id: int, db: Session):
    has_bigfive = db.query(Response.id).filter(
        Response.respondent_id == user_id,
        Response.test_type == "BIGFIVE"
    ).first()
    if has_bigfive:
        return _process_bigfive_results(user_id, db)

    responses = db.query(Response, QuestionnaireItem.dimension).join(
        QuestionnaireItem, Response.item_id == QuestionnaireItem.id
    ).filter(Response.respondent_id == user_id).all()

    # Parâmetros Populacionais de Referência para calibração de Score-Z
    # Podem ser recalculados dinamicamente via cron/worker
    # DISC Média e Desvio Padrão populacionais (escala -24 a 24)
    disc_ref = {
        "D": {"mean": 1.5, "std": 5.5},
        "I": {"mean": 2.5, "std": 4.8},
        "S": {"mean": -0.8, "std": 6.2},
        "C": {"mean": 0.2, "std": 5.8}
    }
    
    # Spranger Média e Desvio Padrão (escala 4 a 24)
    spranger_ref = {
        "teorico": {"mean": 14.5, "std": 3.8},
        "economico": {"mean": 13.8, "std": 3.2},
        "estetico": {"mean": 11.2, "std": 4.1},
        "social": {"mean": 15.1, "std": 3.5},
        "individualista": {"mean": 14.0, "std": 3.9},
        "regulador": {"mean": 13.5, "std": 3.4}
    }

    # 1. Agregação DISC
    disc_raw = {
        "natural": {"D": 0.0, "I": 0.0, "S": 0.0, "C": 0.0},
        "adaptado": {"D": 0.0, "I": 0.0, "S": 0.0, "C": 0.0}
    }
    for resp, dim in responses:
        if resp.test_type == "DISC":
            phase = resp.phase
            # O valor do DISC é +1 (Mais), -1 (Menos)
            disc_raw[phase][dim] = disc_raw[phase].get(dim, 0.0) + (resp.value * resp.respondent.responses[0].item_id * 0.0 + resp.value)

    # Normalização DISC (Score-Z -> Percentil)
    disc_percentile = {"natural": {}, "adaptado": {}}
    for phase in ["natural", "adaptado"]:
        for dim in ["D", "I", "S", "C"]:
            raw = disc_raw[phase][dim]
            mean = disc_ref[dim]["mean"]
            std = disc_ref[dim]["std"]
            disc_percentile[phase][dim] = raw_to_percentile(raw, mean, std)

    # 2. Gasto Energético e Risco de Burnout (Distância Euclidiana)
    nat_vec = [disc_percentile["natural"][d] for d in ["D", "I", "S", "C"]]
    ada_vec = [disc_percentile["adaptado"][d] for d in ["D", "I", "S", "C"]]
    burnout_dist = calculate_euclidean_distance(nat_vec, ada_vec)
    
    # Risco de Burnout: Limiar de distância (em percentis, máximo teórico de 200)
    # Se distância > 40 percentis cumulativos (desvio-padrão equivalente a 2.0 populacional)
    if burnout_dist >= 55.0:
        burnout_risk = "Alto"
    elif burnout_dist >= 35.0:
        burnout_risk = "Médio"
    else:
        burnout_risk = "Baixo"

    # 3. Agregação Spranger (Motivadores)
    spranger_raw = {"teorico": 0.0, "economico": 0.0, "estetico": 0.0, "social": 0.0, "individualista": 0.0, "regulador": 0.0}
    for resp, dim in responses:
        if resp.test_type == "SPRANGER":
            # Likert 1-6
            spranger_raw[dim] = spranger_raw.get(dim, 0.0) + resp.value

    # Normalização Spranger (Score-Z -> Percentil)
    spranger_percentile = {}
    for dim in spranger_raw.keys():
        raw = spranger_raw[dim]
        mean = spranger_ref[dim]["mean"]
        std = spranger_ref[dim]["std"]
        spranger_percentile[dim] = raw_to_percentile(raw, mean, std)

    # 4. Agregação JUNG
    jung_raw = {"E": 0.0, "I": 0.0, "S": 0.0, "N": 0.0, "T": 0.0, "F": 0.0, "J": 0.0, "P": 0.0}
    for resp, dim in responses:
        if resp.test_type == "JUNG":
            # Likert 1-6
            jung_raw[dim] = jung_raw.get(dim, 0.0) + resp.value

    # Calcula percentual de cada polo na dicotomia
    jung_pct = {}
    dicotonomies = [("E", "I"), ("S", "N"), ("T", "F"), ("J", "P")]
    for p1, p2 in dicotonomies:
        total = jung_raw[p1] + jung_raw[p2]
        if total == 0:
            jung_pct[p1] = 50.0
            jung_pct[p2] = 50.0
        else:
            jung_pct[p1] = round((jung_raw[p1] / total) * 100, 2)
            jung_pct[p2] = round(100.0 - jung_pct[p1], 2)

    # Derivação do Tipo Dominante (ex: INTJ)
    dominant_type = ""
    dominant_type += "E" if jung_pct["E"] >= 50.0 else "I"
    dominant_type += "S" if jung_pct["S"] >= 50.0 else "N"
    dominant_type += "T" if jung_pct["T"] >= 50.0 else "F"
    dominant_type += "J" if jung_pct["J"] >= 50.0 else "P"

    # 5. Detecção de Zonas de Fricção
    frictions = detect_frictions(disc_percentile["natural"], spranger_percentile, jung_pct)

    # Salva ou Atualiza os Resultados Psicométricos
    # INVARIANTE F5 (teste-reteste): NUNCA apagar resultados Big Five. O caminho Big Five é
    # append-only (early return has_bigfive -> _process_bigfive_results). Este delete pertence
    # ao caminho consolidado (sem Big Five) e remove APENAS resultados consolidados/legados
    # (bigfive_percentis IS NULL), preservando todo o histórico Big Five que sustenta a
    # exportação e o teste-reteste.
    db.query(PsychometricResult).filter(
        PsychometricResult.respondent_id == user_id,
        PsychometricResult.bigfive_percentis.is_(None)
    ).delete(synchronize_session=False)
    
    result = PsychometricResult(
        respondent_id=user_id,
        natural_raw_d=disc_raw["natural"]["D"],
        natural_raw_i=disc_raw["natural"]["I"],
        natural_raw_s=disc_raw["natural"]["S"],
        natural_raw_c=disc_raw["natural"]["C"],
        adapted_raw_d=disc_raw["adaptado"]["D"],
        adapted_raw_i=disc_raw["adaptado"]["I"],
        adapted_raw_s=disc_raw["adaptado"]["S"],
        adapted_raw_c=disc_raw["adaptado"]["C"],
        natural_percentile_d=disc_percentile["natural"]["D"],
        natural_percentile_i=disc_percentile["natural"]["I"],
        natural_percentile_s=disc_percentile["natural"]["S"],
        natural_percentile_c=disc_percentile["natural"]["C"],
        adapted_percentile_d=disc_percentile["adaptado"]["D"],
        adapted_percentile_i=disc_percentile["adaptado"]["I"],
        adapted_percentile_s=disc_percentile["adaptado"]["S"],
        adapted_percentile_c=disc_percentile["adaptado"]["C"],
        burnout_distance=burnout_dist,
        burnout_risk=burnout_risk,
        spranger_percentile_teorico=spranger_percentile["teorico"],
        spranger_percentile_economico=spranger_percentile["economico"],
        spranger_percentile_estetico=spranger_percentile["estetico"],
        spranger_percentile_social=spranger_percentile["social"],
        spranger_percentile_individualista=spranger_percentile["individualista"],
        spranger_percentile_regulador=spranger_percentile["regulador"],
        jung_dominant_type=dominant_type,
        jung_scores=jung_pct,
        frictions=frictions
    )
    db.add(result)
    db.commit()

# ==============================================================================
# ROTAS DE RESULTADOS E INTELIGÊNCIA ARTIFICIAL
# ==============================================================================

def _reflection_payload(result_id: int, db: Session) -> Dict[str, Optional[str]]:
    reflection = db.query(PersonalReflection).filter(
        PersonalReflection.result_id == result_id
    ).first()
    return {
        "self_understanding_goal": reflection.self_understanding_goal if reflection else None,
        "current_pattern_to_observe": reflection.current_pattern_to_observe if reflection else None
    }


@app.patch("/results/{result_id}/reflections")
def update_result_reflections(
    result_id: int,
    submission: ReflectionSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = db.query(PsychometricResult).filter(
        PsychometricResult.id == result_id,
        PsychometricResult.respondent_id == current_user.id
    ).first()
    if not result:
        raise HTTPException(status_code=404, detail="Aplicação não encontrada.")

    self_goal = (submission.self_understanding_goal or "").strip() or None
    pattern = (submission.current_pattern_to_observe or "").strip() or None
    reflection = db.query(PersonalReflection).filter(
        PersonalReflection.result_id == result.id,
        PersonalReflection.respondent_id == current_user.id
    ).first()
    if reflection:
        reflection.self_understanding_goal = self_goal
        reflection.current_pattern_to_observe = pattern
    else:
        reflection = PersonalReflection(
            respondent_id=current_user.id,
            result_id=result.id,
            self_understanding_goal=self_goal,
            current_pattern_to_observe=pattern
        )
        db.add(reflection)

    db.commit()
    return {
        "result_id": result.id,
        "reflections": _reflection_payload(result.id, db)
    }


@app.get("/results/me")
def get_my_results(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = db.query(PsychometricResult).filter(
        PsychometricResult.respondent_id == current_user.id
    ).order_by(PsychometricResult.created_at.desc()).first()
    if not result:
        raise HTTPException(status_code=404, detail="Você ainda não concluiu todas as fases do teste.")

    if result.bigfive_percentis:
        sem = standard_error_of_measurement(sd=15.0, reliability=0.84)
        fatores = {}
        nomes = {
            "O": "Abertura",
            "C": "Conscienciosidade",
            "E": "Extroversão",
            "A": "Amabilidade",
            "N": "Neuroticismo"
        }
        raw_scores = {
            "O": result.bigfive_O,
            "C": result.bigfive_C,
            "E": result.bigfive_E,
            "A": result.bigfive_A,
            "N": result.bigfive_N
        }
        result_count = db.query(PsychometricResult).filter(
            PsychometricResult.respondent_id == current_user.id,
            PsychometricResult.bigfive_percentis.isnot(None)
        ).count()
        history_entries = _bigfive_history_entries(current_user.id, db)
        is_first_assessment = settings.NORM_MODE == "intra" and result_count <= 1
        warnings = [NON_DIAGNOSTIC_NOTICE]
        if is_first_assessment:
            warnings.append("Primeira aplicação — linha de base interna criada. Ainda não há histórico suficiente para comparação intraindividual.")
        if settings.NORM_MODE == "public":
            warnings.append(
                "Percentis calculados com base em norma pública exploratória disponível no projeto. "
                "Este resultado não constitui diagnóstico psicológico, laudo psicológico ou teste psicológico validado para uso profissional no Brasil."
            )
        for factor, percentile in result.bigfive_percentis.items():
            ci_low, ci_high = (None, None)
            if percentile is not None:
                ci_low, ci_high = confidence_interval(percentile, sem, bounds=(0, 100))
            fatores[factor] = {
                "label": nomes.get(factor, factor),
                "raw": raw_scores.get(factor, 0.0),
                "mean": round((raw_scores.get(factor, 0.0) or 0.0) / 10.0, 2),
                "max_raw": 50,
                "percentile": percentile,
                "ci_low": ci_low,
                "ci_high": ci_high
            }

        bigfive_dict = {
            "factors": fatores,
            "norm_mode": settings.NORM_MODE,
            "norm_label": "primeira aplicação — linha de base interna criada" if is_first_assessment else _bigfive_norm_label(),
            "is_first_assessment": is_first_assessment,
            "has_population_norm": settings.NORM_MODE == "public",
            "has_intraindividual_history": result_count > 1,
            "interpretation_confidence": "baseline" if is_first_assessment else "exploratory",
            "warnings": warnings,
            "measured": ["Big Five"],
            "derived": ["Jung contínuo", "DISC derivado", "Spranger derivado"]
        }
        if settings.NORM_MODE == "public":
            norm_src = load_norm_source(settings.NORM_SOURCE)
            bigfive_dict["norm_info"] = {
                "mode": "public",
                "source": settings.NORM_SOURCE,
                "n": norm_src["n"]
            }

        return {
            "result_id": result.id,
            "candidate": current_user.full_name,
            "date": result.created_at,
            "bigfive": bigfive_dict,
            "jung_continuo": result.jung_continuo,
            "disc": {
                "natural": {"D": result.natural_percentile_d, "I": result.natural_percentile_i, "S": result.natural_percentile_s, "C": result.natural_percentile_c},
                "derived_from": "BIGFIVE",
                "aviso": "DISC derivado — leitura ilustrativa baseada nos fatores Big Five. Não substitui um instrumento DISC validado."
            },
            "spranger": {
                "teorico": result.spranger_percentile_teorico,
                "economico": result.spranger_percentile_economico,
                "estetico": result.spranger_percentile_estetico,
                "social": result.spranger_percentile_social,
                "individualista": result.spranger_percentile_individualista,
                "regulador": result.spranger_percentile_regulador,
                "derived_from": "BIGFIVE",
                "aviso": "Spranger derivado — leitura ilustrativa baseada nos fatores Big Five. Não substitui um instrumento motivacional validado."
            },
            "quality_label": result.quality_label,
            "frictions": result.frictions,
            "metadata": {
                "norm_mode": settings.NORM_MODE,
                "is_first_assessment": is_first_assessment,
                "has_population_norm": settings.NORM_MODE == "public",
                "has_intraindividual_history": result_count > 1,
                "interpretation_confidence": "baseline" if is_first_assessment else "exploratory",
                "warnings": warnings,
                "norm_label": bigfive_dict["norm_label"],
            },
            "history": history_entries,
            "reflections": _reflection_payload(result.id, db),
            "notice": NON_DIAGNOSTIC_NOTICE
        }
        
    return {
        "result_id": result.id,
        "candidate": current_user.full_name,
        "date": result.created_at,
        "disc": {
            "natural": {"D": result.natural_percentile_d, "I": result.natural_percentile_i, "S": result.natural_percentile_s, "C": result.natural_percentile_c},
            "adapted": {"D": result.adapted_percentile_d, "I": result.adapted_percentile_i, "S": result.adapted_percentile_s, "C": result.adapted_percentile_c},
            "burnout_distance": result.burnout_distance,
            "burnout_risk": result.burnout_risk
        },
        "spranger": {
            "teorico": result.spranger_percentile_teorico,
            "economico": result.spranger_percentile_economico,
            "estetico": result.spranger_percentile_estetico,
            "social": result.spranger_percentile_social,
            "individualista": result.spranger_percentile_individualista,
            "regulador": result.spranger_percentile_regulador,
            "aviso": "Estimativa ilustrativa derivada do Big Five — não é instrumento independente validado."
        },
        "jung": {
            "dominant_type": result.jung_dominant_type,
            "scores": result.jung_scores
        },
        "reflections": _reflection_payload(result.id, db),
        "frictions": result.frictions
    }

@app.get("/results/report")
def get_narrative_report(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = db.query(PsychometricResult).filter(
        PsychometricResult.respondent_id == current_user.id
    ).order_by(PsychometricResult.created_at.desc()).first()
    if not result:
        raise HTTPException(status_code=404, detail="Resultados psicométricos não disponíveis.")
        
    report = db.query(Report).filter(Report.result_id == result.id).first()
    if report and report.status == "completed" and (not result.bigfive_percentis or "### Limites desta avaliação" in (report.narrative_text or "")):
        return {"report": report.narrative_text}
        
    # Se não houver, gera na hora (ou simula)
    # 1. Agrega alertas de fraude na telemetria
    telemetry_sessions = db.query(TelemetrySession).filter(TelemetrySession.respondent_id == current_user.id).all()
    alerts = []
    for ts in telemetry_sessions:
        if ts.is_fraud_suspect and ts.fraud_reasons:
            alerts.extend(ts.fraud_reasons)
            
    # 2. Chama a inteligência artificial (Gemini)
    disc_nat = {"D": result.natural_percentile_d, "I": result.natural_percentile_i, "S": result.natural_percentile_s, "C": result.natural_percentile_c}
    disc_ada = {"D": result.adapted_percentile_d, "I": result.adapted_percentile_i, "S": result.adapted_percentile_s, "C": result.adapted_percentile_c}
    spranger_scores = {
        "teorico": result.spranger_percentile_teorico,
        "economico": result.spranger_percentile_economico,
        "estetico": result.spranger_percentile_estetico,
        "social": result.spranger_percentile_social,
        "individualista": result.spranger_percentile_individualista,
        "regulador": result.spranger_percentile_regulador
    }
    bigfive_factors = None
    emotional_stability = None
    if result.bigfive_percentis:
        sem = standard_error_of_measurement(sd=15.0, reliability=0.84)
        raw_scores = {
            "O": result.bigfive_O,
            "C": result.bigfive_C,
            "E": result.bigfive_E,
            "A": result.bigfive_A,
            "N": result.bigfive_N
        }
        bigfive_factors = {}
        for factor, score in result.bigfive_percentis.items():
            ci_low, ci_high = (None, None)
            if score is not None:
                ci_low, ci_high = confidence_interval(score, sem, bounds=(0, 100))
            bigfive_factors[factor] = {
                "raw": raw_scores.get(factor, 0.0),
                "mean": round((raw_scores.get(factor, 0.0) or 0.0) / 10.0, 2),
                "percentile": score,
                "ci_low": ci_low,
                "ci_high": ci_high
            }
        emotional_stability = (result.jung_continuo or {}).get("estabilidade_emocional")
    
    narrative = generate_psychometric_report(
        candidate_name=current_user.full_name,
        disc_natural=disc_nat,
        disc_adapted=disc_ada,
        burnout_distance=result.burnout_distance,
        burnout_risk=result.burnout_risk,
        spranger_scores=spranger_scores,
        jung_type=result.jung_dominant_type,
        jung_scores=result.jung_scores,
        frictions=result.frictions,
        telemetry_alerts=alerts,
        bigfive_factors=bigfive_factors,
        jung_continuo=result.jung_continuo,
        emotional_stability=emotional_stability,
        quality_label=result.quality_label
    )
    
    # Salva relatório no BD
    if report:
        db.query(Report).filter(Report.id == report.id).delete()
    
    new_report = Report(
        respondent_id=current_user.id,
        result_id=result.id,
        status="completed",
        narrative_text=narrative
    )
    db.add(new_report)
    db.commit()
    
    return {"report": narrative}

# ==============================================================================
# ROTAS DO RH (EMPRESAS / GESTÃO DE VAGAS)
# ==============================================================================

@app.post("/rh/jobs")
def create_job(job_in: JobCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ["hr", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso restrito ao RH da empresa.")
        
    job = Job(
        tenant_id=current_user.tenant_id,
        title=job_in.title,
        description=job_in.description,
        target_d=job_in.target_d,
        target_i=job_in.target_i,
        target_s=job_in.target_s,
        target_c=job_in.target_c,
        target_spranger=job_in.target_spranger,
        target_jung=job_in.target_jung
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@app.get("/rh/jobs")
def list_jobs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ["hr", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso restrito ao RH da empresa.")
        
    return db.query(Job).filter(Job.tenant_id == current_user.tenant_id).all()

@app.get("/rh/matching/{job_id}")
def get_job_matching(job_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Executa o algoritmo de Similaridade de Cossenos entre o perfil ideal da vaga
    e todos os candidatos do Tenant que concluíram a avaliação psicométrica.
    """
    if current_user.role not in ["hr", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso restrito ao RH da empresa.")
        
    job = db.query(Job).filter(Job.id == job_id, Job.tenant_id == current_user.tenant_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Vaga não encontrada.")
        
    candidates_results = db.query(PsychometricResult, User.full_name, User.email).join(
        User, PsychometricResult.respondent_id == User.id
    ).filter(User.tenant_id == current_user.tenant_id).all()

    v_job = [job.target_d, job.target_i, job.target_s, job.target_c]
    
    rankings = []
    for res, name, email in candidates_results:
        # Vetor do candidato (usamos percentil natural)
        # Convertemos 0-100 para escala 0.0-1.0
        v_cand = [
            res.natural_percentile_d / 100.0,
            res.natural_percentile_i / 100.0,
            res.natural_percentile_s / 100.0,
            res.natural_percentile_c / 100.0
        ]
        
        sim = calculate_cosine_similarity(v_cand, v_job)
        
        # Similaridade estendida opcional de motivadores se houver
        # Podemos mesclar 80% peso do DISC e 20% peso dos motivadores
        rankings.append({
            "respondent_id": res.respondent_id,
            "name": name,
            "email": email,
            "matching_score": round(sim * 100, 2),
            "burnout_risk": res.burnout_risk,
            "dominant_type": res.jung_dominant_type
        })
        
    # Ordena pelo maior score de matching
    rankings.sort(key=lambda x: x["matching_score"], reverse=True)
    return rankings

@app.get("/rh/team-matrix")
def get_team_matrix(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Agrega as pontuações dos candidatos do time e plota as variáveis para o Heatmap.
    Eixo X: Foco em Ação (Dominância + Influência) vs Foco em Relações (Estabilidade + Conformidade)
    """
    if current_user.role not in ["hr", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso restrito ao RH da empresa.")
        
    results = db.query(PsychometricResult, User.full_name).join(
        User, PsychometricResult.respondent_id == User.id
    ).filter(User.tenant_id == current_user.tenant_id).all()
    
    points = []
    for res, name in results:
        # Plotagem Bidimensional Simples para o Matrix Heatmap
        # Eixo X: Orientação a Pessoas (I + S) vs Orientação a Tarefas (D + C)
        # Eixo Y: Ritmo Rápido (D + I) vs Ritmo Planejado (S + C)
        pessoas = res.natural_percentile_i + res.natural_percentile_s
        tarefas = res.natural_percentile_d + res.natural_percentile_c
        fast_pace = res.natural_percentile_d + res.natural_percentile_i
        slow_pace = res.natural_percentile_s + res.natural_percentile_c
        
        x = round((pessoas - tarefas) / 2.0, 2)  # -50 a 50
        y = round((fast_pace - slow_pace) / 2.0, 2) # -50 a 50
        
        points.append({
            "name": name,
            "x": x,
            "y": y,
            "dominant": res.jung_dominant_type,
            "risk": res.burnout_risk
        })
        
    return points

# ==============================================================================
# ROTA ADMINISTRATIVA (BACKOFFICE GLOBAL)
# ==============================================================================

@app.get("/admin/stats")
def get_global_statistics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso exclusivo ao Administrador Global.")
        
    results = db.query(PsychometricResult).all()
    if not results:
        return {"total_evaluations": 0, "gaussian": []}
        
    scores_d = [r.natural_raw_d for r in results]
    
    # Gera 15 bins para a distribuição gaussiana do eixo D em Python puro
    min_val = min(scores_d)
    max_val = max(scores_d)
    if min_val == max_val:
        min_val -= 1.0
        max_val += 1.0
    
    bin_width = (max_val - min_val) / 15
    bin_edges = [min_val + i * bin_width for i in range(16)]
    hist = [0] * 15
    for val in scores_d:
        bin_idx = int((val - min_val) / bin_width)
        if bin_idx >= 15:
            bin_idx = 14
        elif bin_idx < 0:
            bin_idx = 0
        hist[bin_idx] += 1

    gaussian_points = []
    for i in range(15):
        gaussian_points.append({
            "x": round(float((bin_edges[i] + bin_edges[i+1]) / 2.0), 2),
            "y": int(hist[i])
        })
        
    omega_bigfive = {}
    for factor in ["O", "C", "E", "A", "N"]:
        factor_rows = db.query(Response).join(
            QuestionnaireItem, Response.item_id == QuestionnaireItem.id
        ).filter(
            Response.test_type == "BIGFIVE",
            QuestionnaireItem.dimension == factor
        ).all()

        user_ids = sorted(set(r.respondent_id for r in factor_rows))
        item_ids = sorted(set(r.item_id for r in factor_rows))
        omega_value = 0.0
        if len(user_ids) > 3 and len(item_ids) > 3:
            matrix = [[0.0] * len(item_ids) for _ in range(len(user_ids))]
            user_to_idx = {uid: idx for idx, uid in enumerate(user_ids)}
            item_to_idx = {iid: idx for idx, iid in enumerate(item_ids)}
            for r in factor_rows:
                matrix[user_to_idx[r.respondent_id]][item_to_idx[r.item_id]] = r.value
            omega_value = mcdonald_omega(matrix)
        omega_bigfive[factor] = omega_value

    return {
        "total_evaluations": len(results),
        "omega_bigfive": omega_bigfive,
        "gaussian": gaussian_points
    }


@app.get("/admin/export/bigfive")
def export_bigfive_csv(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso exclusivo ao Administrador Global.")

    rows = db.query(PsychometricResult).filter(
        PsychometricResult.bigfive_percentis.isnot(None)
    ).order_by(PsychometricResult.created_at.asc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "respondent_id", "applied_at",
        "O_raw", "C_raw", "E_raw", "A_raw", "N_raw",
        "O_pct", "C_pct", "E_pct", "A_pct", "N_pct",
        "quality_label"
    ])
    for r in rows:
        pct = r.bigfive_percentis or {}
        writer.writerow([
            r.respondent_id,
            r.created_at.isoformat() if r.created_at else "",
            r.bigfive_O, r.bigfive_C, r.bigfive_E, r.bigfive_A, r.bigfive_N,
            pct.get("O", ""), pct.get("C", ""), pct.get("E", ""),
            pct.get("A", ""), pct.get("N", ""),
            r.quality_label or ""
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=\"bigfive_export.csv\""}
    )
