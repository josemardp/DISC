from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.app.database import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="tenant", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)  # Null para Super Admin global
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default="respondent")  # admin, hr, respondent
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    tenant = relationship("Tenant", back_populates="users")
    responses = relationship("Response", back_populates="respondent", cascade="all, delete-orphan")
    telemetry_sessions = relationship("TelemetrySession", back_populates="respondent", cascade="all, delete-orphan")
    psychometric_results = relationship("PsychometricResult", back_populates="respondent", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="respondent", cascade="all, delete-orphan")
    personal_reflections = relationship("PersonalReflection", back_populates="respondent", cascade="all, delete-orphan")

class QuestionnaireItem(Base):
    __tablename__ = "questionnaire_items"

    id = Column(Integer, primary_key=True, index=True)  # Ex: 101, 102
    block_number = Column(Integer, index=True, nullable=False)  # Bloco 1 a 24
    test_type = Column(String, index=True, nullable=False)  # DISC, SPRANGER, JUNG
    dimension = Column(String, nullable=False)  # D, I, S, C / Teorico, Economico, etc. / E, I, S, N, T, F, J, P
    item_text = Column(String, nullable=False)  # Adjetivo ou afirmação
    weight = Column(Float, default=1.0)  # Peso psicométrico
    reverse_keyed = Column(Boolean, default=False)

class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    respondent_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("questionnaire_items.id"), nullable=False)
    block_number = Column(Integer, nullable=False)
    test_type = Column(String, nullable=False)  # DISC, SPRANGER, JUNG
    phase = Column(String, nullable=False)  # natural, adaptado
    value = Column(Integer, nullable=False)  # DISC: +1 (Mais), -1 (Menos), 0 (Neutro). Spranger/Jung: Likert 1-6.
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    respondent = relationship("User", back_populates="responses")

class TelemetrySession(Base):
    __tablename__ = "telemetry_sessions"

    id = Column(Integer, primary_key=True, index=True)
    respondent_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    test_type = Column(String, nullable=False)  # DISC, SPRANGER, JUNG
    phase = Column(String, nullable=False)  # natural, adaptado
    ttfc_avg = Column(Float, nullable=False)  # Time to First Click médio (ms)
    irt_avg = Column(Float, nullable=False)   # Item Response Time médio (ms)
    rvi_count = Column(Integer, default=0)    # Quantidade de mudanças de opção
    is_fraud_suspect = Column(Boolean, default=False)
    fraud_reasons = Column(JSON, nullable=True)  # Lista de motivos (LinearPattern, SocialDesirability)
    raw_telemetry = Column(JSON, nullable=True)  # Registro detalhado por item
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    respondent = relationship("User", back_populates="telemetry_sessions")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Perfil ideal da Vaga para Job Matching (Valores Vetoriais 0.0 a 1.0 ou Scores de Referência)
    target_d = Column(Float, default=0.5)
    target_i = Column(Float, default=0.5)
    target_s = Column(Float, default=0.5)
    target_c = Column(Float, default=0.5)
    
    # Demais eixos em formato JSON para flexibilidade
    target_spranger = Column(JSON, nullable=True)  # {"teorico": 40, "economico": 50, ...}
    target_jung = Column(JSON, nullable=True)      # {"E": 60, "I": 40, "S": 50, "N": 50, "T": 60, "F": 40, "J": 70, "P": 30}
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    tenant = relationship("Tenant", back_populates="jobs")

class PsychometricResult(Base):
    __tablename__ = "psychometric_results"

    id = Column(Integer, primary_key=True, index=True)
    respondent_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # DISC Raw Scores (Perfil Natural)
    natural_raw_d = Column(Float, default=0.0)
    natural_raw_i = Column(Float, default=0.0)
    natural_raw_s = Column(Float, default=0.0)
    natural_raw_c = Column(Float, default=0.0)

    # DISC Raw Scores (Perfil Adaptado)
    adapted_raw_d = Column(Float, default=0.0)
    adapted_raw_i = Column(Float, default=0.0)
    adapted_raw_s = Column(Float, default=0.0)
    adapted_raw_c = Column(Float, default=0.0)

    # DISC Percentis Normalizados populacionais (0 a 100)
    natural_percentile_d = Column(Float, default=0.0)
    natural_percentile_i = Column(Float, default=0.0)
    natural_percentile_s = Column(Float, default=0.0)
    natural_percentile_c = Column(Float, default=0.0)

    adapted_percentile_d = Column(Float, default=0.0)
    adapted_percentile_i = Column(Float, default=0.0)
    adapted_percentile_s = Column(Float, default=0.0)
    adapted_percentile_c = Column(Float, default=0.0)

    # Desvio Temporal (Distância Euclidiana Natural vs Adaptado)
    burnout_distance = Column(Float, default=0.0)
    burnout_risk = Column(String, default="Baixo")  # Baixo, Médio, Alto

    # Motivadores Spranger (Valores Brutos normalizados em percentis)
    spranger_percentile_teorico = Column(Float, default=0.0)
    spranger_percentile_economico = Column(Float, default=0.0)
    spranger_percentile_estetico = Column(Float, default=0.0)
    spranger_percentile_social = Column(Float, default=0.0)
    spranger_percentile_individualista = Column(Float, default=0.0)
    spranger_percentile_regulador = Column(Float, default=0.0)

    # Jung Tipos Cognitivos
    jung_dominant_type = Column(String, nullable=True)  # ex: INTJ, ENFP
    jung_scores = Column(JSON, nullable=True)  # Scores brutos detalhados por polo {"E": 20, "I": 12, ...}

    # Núcleo Big Five (IPIP)
    bigfive_O = Column(Float, default=0.0)
    bigfive_C = Column(Float, default=0.0)
    bigfive_E = Column(Float, default=0.0)
    bigfive_A = Column(Float, default=0.0)
    bigfive_N = Column(Float, default=0.0)
    bigfive_percentis = Column(JSON, nullable=True)
    jung_continuo = Column(JSON, nullable=True)
    quality_label = Column(String, nullable=True)
    
    # Fricções identificadas
    frictions = Column(JSON, nullable=True)  # Lista de alertas detectados (Fricção de Execução, Fricção de Comunicação)

    respondent = relationship("User", back_populates="psychometric_results")
    reports = relationship("Report", back_populates="result", cascade="all, delete-orphan")
    personal_reflection = relationship("PersonalReflection", back_populates="result", uselist=False, cascade="all, delete-orphan")

class PersonalReflection(Base):
    __tablename__ = "personal_reflections"

    id = Column(Integer, primary_key=True, index=True)
    respondent_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    result_id = Column(Integer, ForeignKey("psychometric_results.id"), nullable=False, unique=True, index=True)
    self_understanding_goal = Column(Text, nullable=True)
    current_pattern_to_observe = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    respondent = relationship("User", back_populates="personal_reflections")
    result = relationship("PsychometricResult", back_populates="personal_reflection")

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    respondent_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    result_id = Column(Integer, ForeignKey("psychometric_results.id"), nullable=False)
    status = Column(String, default="pending")  # pending, generating, completed, failed
    narrative_text = Column(Text, nullable=True)  # Texto markdown gerado pelo Gemini
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    respondent = relationship("User", back_populates="reports")
    result = relationship("PsychometricResult", back_populates="reports")
