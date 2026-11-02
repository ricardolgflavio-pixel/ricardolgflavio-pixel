"""Esquema de ingestão RAG com Compliance as Code (Pydantic v2 + pgvector).

Resumo executivo
----------------
Este módulo transforma regras jurídicas em *contratos de dados executáveis*.
Nenhum fragmento técnico automotivo chega à tabela vetorial (``pgvector``) sem
antes comprovar, de forma verificável e auditável:

1. **Origem lícita** (``SourceType``): catálogo aberto de fabricante, padrão
   SAE/ISO ou telemetria interna própria (Ordens de Serviço e scanner OBD2);
2. **Natureza factual** do conteúdo (Ohms, Volts, bar, pinout, códigos DTC,
   torques em Nm) — dados técnicos funcionais, sem a originalidade que
   caracteriza obra protegida pela Lei 9.610/98 (Lei de Direitos Autorais);
3. **Método de coleta permitido** — *scraping* de bases proprietárias fechadas
   (ex.: Doutor-IE, Simplo) é proibido por arquitetura, em respeito à
   Lei 9.609/98 (Lei do Software), à Lei 9.610/98 e aos termos de uso;
4. **Privacy by Design** (LGPD, Lei 13.709/2018): telemetria interna exige base
   legal declarada, ``tenant_id`` e ausência de identificadores pessoais
   (CPF, e-mail, telefone, placa de veículo);
5. **Integridade vetorial**: dimensão do *embedding* e valores finitos.

Os controles espelham o *gate* de ingestão do projeto AutoTech AI OS e podem
ser executados diretamente: ``python showcase/rag_legal_ingestion_schema.py``.

Observação: o vetor de demonstração é determinístico e **não** representa um
modelo de *embedding* real; em produção substitua por um provedor aprovado.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import struct
import sys
import uuid
from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Final
from urllib.parse import urlparse

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    computed_field,
    field_validator,
    model_validator,
)

EMBEDDING_DIM: Final[int] = 1536
MAX_CHUNK_CHARS: Final[int] = 1200

INSERT_CHUNK_SQL: Final[str] = (
    "INSERT INTO technical_chunks "
    "(chunk_id, tenant_id, content, content_class, source_type, source_name, "
    "license_basis, audit_id, fingerprint, embedding) "
    "VALUES (%(chunk_id)s, %(tenant_id)s, %(content)s, %(content_class)s, "
    "%(source_type)s, %(source_name)s, %(license_basis)s, %(audit_id)s, "
    "%(fingerprint)s, %(embedding)s::vector) "
    "ON CONFLICT (fingerprint) DO NOTHING"
)

# Domínios (sufixos) de fabricantes cujos catálogos técnicos públicos foram auditados.
AUDITED_CATALOG_DOMAINS: Final[frozenset[str]] = frozenset(
    {
        "bosch.com",
        "bosch.com.br",
        "boschaftermarket.com",
        "magnetimarelli.com",
        "magnetimarelli-aftermarket.com",
        "ngk.com.br",
        "ngkntk.com",
        "denso.com",
        "valeo.com",
    }
)
# Bases proprietárias fechadas: ingestão e coleta automatizada proibidas.
BLOCKED_PROPRIETARY_MARKERS: Final[tuple[str, ...]] = ("doutor-ie", "doutorie", "simplo")

PROTECTED_WORK_MARKERS: Final[re.Pattern[str]] = re.compile(
    r"(?:©|\(c\)\s*\d{4}|all rights reserved|todos os direitos reservados|"
    r"proibida a reprodu[cç][aã]o|proprietary and confidential|uso restrito)",
    re.IGNORECASE,
)
STANDARD_REFERENCE: Final[re.Pattern[str]] = re.compile(
    r"^(?:SAE\s+J\d{3,5}(?:-\d+)?|ISO\s+\d{4,5}(?:-\d+)?)$"
)
DTC_CODE: Final[re.Pattern[str]] = re.compile(r"\b[PBCU][0-3][0-9A-F]{3}\b")
PINOUT: Final[re.Pattern[str]] = re.compile(r"\b(?:pin|pino|terminal)\s*\d{1,3}\b", re.IGNORECASE)
ELECTRICAL_UNIT: Final[re.Pattern[str]] = re.compile(
    r"\d+(?:[.,]\d+)?\s?(?:m|k|M)?(?:Ω|ohms?|V|A|Hz)(?!\w)", re.IGNORECASE
)
PRESSURE_UNIT: Final[re.Pattern[str]] = re.compile(
    r"\d+(?:[.,]\d+)?\s?(?:bar|kPa|MPa|psi)(?!\w)", re.IGNORECASE
)
TORQUE_UNIT: Final[re.Pattern[str]] = re.compile(r"\d+(?:[.,]\d+)?\s?(?:N\.?m|kgf\.?m)(?!\w)")

PII_PATTERNS: Final[dict[str, re.Pattern[str]]] = {
    "CPF": re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"),
    "e-mail": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "telefone": re.compile(r"(?:\+?55\s?)?\(?\d{2}\)?\s?9?\d{4}[-\s]?\d{4}\b"),
    "placa": re.compile(r"\b[A-Z]{3}-?\d[A-Z0-9]\d{2}\b"),
}


class SourceType(StrEnum):
    """Origens lícitas e auditadas de dados técnicos para o RAG."""

    OPEN_CATALOG = "catalogo_aberto"
    SAE_ISO_STANDARD = "padrao_sae_iso"
    INTERNAL_TELEMETRY = "telemetria_interna"


class LicenseBasis(StrEnum):
    """Fundamento jurídico que legitima o uso do dado."""

    PUBLIC_TECHNICAL_FACT = "fato_tecnico_dominio_publico"
    MANUFACTURER_OPEN_CATALOG = "catalogo_aberto_fabricante"
    STANDARD_FACTUAL_REFERENCE = "referencia_factual_padrao"
    OWN_DATA = "dado_proprio_titularidade_interna"


class CollectionMethod(StrEnum):
    """Método de coleta; ``WEB_SCRAPING`` existe apenas para ser rejeitado."""

    MANUAL_ENTRY = "digitacao_manual_auditada"
    OFFICIAL_DOWNLOAD = "download_oficial_catalogo"
    OBD2_SCANNER = "scanner_obd2_xtool"
    SERVICE_ORDER_EXPORT = "exportacao_ordem_servico"
    WEB_SCRAPING = "web_scraping"


class ContentClass(StrEnum):
    """Classe de conteúdo; somente fatos técnicos são aceitos de fontes externas."""

    DTC_CODE = "codigo_dtc_sae_iso"
    ELECTRICAL_SPEC = "especificacao_eletrica"
    PRESSURE_SPEC = "especificacao_pressao"
    TORQUE_SPEC = "torque_nm"
    PINOUT = "pinagem"
    SERVICE_NARRATIVE = "narrativa_servico_propria"


class LgpdLegalBasis(StrEnum):
    """Bases legais do art. 7º da LGPD admitidas para telemetria interna."""

    CONTRACT_EXECUTION = "execucao_de_contrato"
    LEGITIMATE_INTEREST = "legitimo_interesse"
    CONSENT = "consentimento"


ALLOWED_METHODS: Final[dict[SourceType, frozenset[CollectionMethod]]] = {
    SourceType.OPEN_CATALOG: frozenset(
        {CollectionMethod.OFFICIAL_DOWNLOAD, CollectionMethod.MANUAL_ENTRY}
    ),
    SourceType.SAE_ISO_STANDARD: frozenset({CollectionMethod.MANUAL_ENTRY}),
    SourceType.INTERNAL_TELEMETRY: frozenset(
        {CollectionMethod.OBD2_SCANNER, CollectionMethod.SERVICE_ORDER_EXPORT}
    ),
}
ALLOWED_LICENSES: Final[dict[SourceType, frozenset[LicenseBasis]]] = {
    SourceType.OPEN_CATALOG: frozenset(
        {LicenseBasis.MANUFACTURER_OPEN_CATALOG, LicenseBasis.PUBLIC_TECHNICAL_FACT}
    ),
    SourceType.SAE_ISO_STANDARD: frozenset({LicenseBasis.STANDARD_FACTUAL_REFERENCE}),
    SourceType.INTERNAL_TELEMETRY: frozenset({LicenseBasis.OWN_DATA}),
}
FACTUAL_SIGNALS: Final[dict[ContentClass, tuple[re.Pattern[str], ...]]] = {
    ContentClass.DTC_CODE: (DTC_CODE,),
    ContentClass.ELECTRICAL_SPEC: (ELECTRICAL_UNIT,),
    ContentClass.PRESSURE_SPEC: (PRESSURE_UNIT,),
    ContentClass.TORQUE_SPEC: (TORQUE_UNIT,),
    ContentClass.PINOUT: (PINOUT,),
}


def _host_matches(host: str, domains: Iterable[str]) -> bool:
    return any(host == domain or host.endswith(f".{domain}") for domain in domains)


class SourceProvenance(BaseModel):
    """Cadeia de custódia jurídica do dado (quem, de onde, como e sob qual base)."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    source_type: SourceType
    source_name: str = Field(min_length=3, max_length=120)
    source_uri: str | None = Field(default=None, max_length=2048)
    standard_ref: str | None = Field(default=None, max_length=40)
    license_basis: LicenseBasis
    collection_method: CollectionMethod
    collected_at: datetime
    audited_by: str = Field(min_length=3, max_length=80)
    audit_id: str = Field(pattern=r"^AUD-\d{4}-\d{4,6}$")
    tenant_id: uuid.UUID | None = None
    lgpd_basis: LgpdLegalBasis | None = None
    pii_scrubbed: bool = False

    @field_validator("collected_at")
    @classmethod
    def _timezone_aware_and_not_future(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("collected_at deve conter fuso horário (UTC) para a trilha de auditoria")
        if value > datetime.now(UTC):
            raise ValueError("collected_at não pode estar no futuro")
        return value

    @model_validator(mode="after")
    def _enforce_lawful_origin(self) -> SourceProvenance:
        fingerprint = f"{self.source_name} {self.source_uri or ''}".lower()
        if any(marker in fingerprint for marker in BLOCKED_PROPRIETARY_MARKERS):
            raise ValueError(
                "fonte proprietária fechada bloqueada (Lei 9.609/98 e Lei 9.610/98): "
                "ingestão proibida por política de Compliance as Code"
            )
        if self.collection_method is CollectionMethod.WEB_SCRAPING:
            raise ValueError("coleta por web scraping é proibida; use download oficial ou dado próprio")
        if self.collection_method not in ALLOWED_METHODS[self.source_type]:
            raise ValueError(
                f"método '{self.collection_method.value}' incompatível com a fonte "
                f"'{self.source_type.value}'"
            )
        if self.license_basis not in ALLOWED_LICENSES[self.source_type]:
            raise ValueError(
                f"base de licença '{self.license_basis.value}' não suporta a fonte "
                f"'{self.source_type.value}'"
            )
        self._validate_by_source_type()
        return self

    def _validate_by_source_type(self) -> None:
        if self.source_type is SourceType.OPEN_CATALOG:
            host = (urlparse(self.source_uri or "").hostname or "").lower()
            if not host or not _host_matches(host, AUDITED_CATALOG_DOMAINS):
                raise ValueError("catálogo aberto exige source_uri HTTPS de domínio de fabricante auditado")
            if urlparse(self.source_uri or "").scheme != "https":
                raise ValueError("catálogo aberto exige transporte HTTPS")
        elif self.source_type is SourceType.SAE_ISO_STANDARD:
            if self.standard_ref is None or not STANDARD_REFERENCE.match(self.standard_ref):
                raise ValueError("padrão SAE/ISO exige standard_ref válido (ex.: 'SAE J2012', 'ISO 15031-6')")
        else:
            if self.tenant_id is None:
                raise ValueError("telemetria interna exige tenant_id (segregação multitenant)")
            if self.lgpd_basis is None:
                raise ValueError("telemetria interna exige base legal LGPD declarada (art. 7º)")
            if self.lgpd_basis is LgpdLegalBasis.CONSENT and not self.pii_scrubbed:
                raise ValueError("consentimento não dispensa minimização: pii_scrubbed deve ser verdadeiro")
            if not self.pii_scrubbed:
                raise ValueError("Privacy by Design: dados pessoais devem ser removidos antes da ingestão")


class TechnicalChunk(BaseModel):
    """Fragmento técnico validado, pronto para persistência em ``pgvector``."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    chunk_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    content: str = Field(min_length=5, max_length=MAX_CHUNK_CHARS)
    content_class: ContentClass
    vehicle_make: str = Field(min_length=2, max_length=40)
    vehicle_model: str = Field(min_length=1, max_length=60)
    provenance: SourceProvenance
    embedding: tuple[float, ...] | None = None

    @field_validator("content")
    @classmethod
    def _reject_protected_work_markers(cls, value: str) -> str:
        if PROTECTED_WORK_MARKERS.search(value):
            raise ValueError(
                "marcador de obra protegida detectado (copyright/uso restrito): "
                "trecho não pode ser ingerido"
            )
        return value

    @field_validator("embedding")
    @classmethod
    def _validate_embedding(cls, value: tuple[float, ...] | None) -> tuple[float, ...] | None:
        if value is None:
            return value
        if len(value) != EMBEDDING_DIM:
            raise ValueError(f"embedding deve ter {EMBEDDING_DIM} dimensões, recebido {len(value)}")
        if not all(math.isfinite(component) for component in value):
            raise ValueError("embedding contém NaN ou infinito")
        return value

    @model_validator(mode="after")
    def _enforce_content_policy(self) -> TechnicalChunk:
        is_internal = self.provenance.source_type is SourceType.INTERNAL_TELEMETRY
        if self.content_class is ContentClass.SERVICE_NARRATIVE:
            if not is_internal:
                raise ValueError(
                    "texto narrativo só é admitido de autoria própria (telemetria interna); "
                    "fontes externas aceitam apenas dados técnicos factuais"
                )
        else:
            signals = FACTUAL_SIGNALS[self.content_class]
            if not any(pattern.search(self.content) for pattern in signals):
                raise ValueError(
                    f"conteúdo não evidencia dado factual da classe '{self.content_class.value}'"
                )
        if is_internal:
            leaked = [label for label, pattern in PII_PATTERNS.items() if pattern.search(self.content)]
            if leaked:
                raise ValueError(
                    f"dado pessoal detectado ({', '.join(leaked)}): anonimize antes da ingestão (LGPD)"
                )
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def fingerprint(self) -> str:
        """SHA-256 do conteúdo normalizado, usado para deduplicação idempotente."""
        normalized = " ".join(self.content.lower().split())
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def to_pgvector_row(self) -> dict[str, Any]:
        """Monta os parâmetros nomeados de ``INSERT_CHUNK_SQL`` (sem interpolação de SQL)."""
        if self.embedding is None:
            raise ValueError("embedding ausente: gere o vetor antes de persistir")
        provenance = self.provenance
        return {
            "chunk_id": str(self.chunk_id),
            "tenant_id": str(provenance.tenant_id) if provenance.tenant_id else None,
            "content": self.content,
            "content_class": self.content_class.value,
            "source_type": provenance.source_type.value,
            "source_name": provenance.source_name,
            "license_basis": provenance.license_basis.value,
            "audit_id": provenance.audit_id,
            "fingerprint": self.fingerprint,
            "embedding": "[" + ",".join(f"{component:.8f}" for component in self.embedding) + "]",
        }


class IngestionDecision(BaseModel):
    """Decisão auditável do gate de ingestão para um registro bruto."""

    model_config = ConfigDict(frozen=True)

    accepted: bool
    fingerprint: str | None = None
    audit_id: str | None = None
    reasons: tuple[str, ...] = ()


def deterministic_demo_embedding(text: str) -> tuple[float, ...]:
    """Gera um vetor determinístico (apenas demonstração; não é modelo semântico)."""
    values: list[float] = []
    counter = 0
    while len(values) < EMBEDDING_DIM:
        digest = hashlib.sha256(f"{counter}:{text}".encode()).digest()
        for offset in range(0, len(digest), 4):
            (raw,) = struct.unpack(">I", digest[offset : offset + 4])
            values.append(raw / 2**32 * 2 - 1)
        counter += 1
    return tuple(values[:EMBEDDING_DIM])


def admit(raw: Mapping[str, Any]) -> tuple[TechnicalChunk | None, IngestionDecision]:
    """Executa o gate de conformidade; falha fechada (*fail-closed*) com motivos."""
    audit_id = None
    provenance_raw = raw.get("provenance")
    if isinstance(provenance_raw, Mapping):
        candidate = provenance_raw.get("audit_id")
        audit_id = candidate if isinstance(candidate, str) else None
    try:
        chunk = TechnicalChunk.model_validate(raw)
    except ValidationError as exc:
        reasons = tuple(
            f"{'.'.join(str(part) for part in error['loc']) or '<modelo>'}: "
            f"{error['msg'].removeprefix('Value error, ')}"
            for error in exc.errors()
        )
        return None, IngestionDecision(accepted=False, audit_id=audit_id, reasons=reasons)
    decision = IngestionDecision(
        accepted=True, fingerprint=chunk.fingerprint, audit_id=chunk.provenance.audit_id
    )
    return chunk, decision


def _demo_records() -> list[tuple[str, dict[str, Any]]]:
    now = datetime.now(UTC).isoformat()
    tenant = "0b1f3c52-7c0e-4f8e-9a3d-3f6b9f0a1c11"
    return [
        (
            "Catálogo aberto Bosch — resistência de bobina",
            {
                "content": "Bobina de ignição: resistência primária 0,5 Ω a 20 °C; alimentação 12 V.",
                "content_class": "especificacao_eletrica",
                "vehicle_make": "Fiat",
                "vehicle_model": "Palio 1.0 Fire",
                "provenance": {
                    "source_type": "catalogo_aberto",
                    "source_name": "Bosch Aftermarket — dados técnicos",
                    "source_uri": "https://www.boschaftermarket.com/br/pt/catalogo",
                    "license_basis": "catalogo_aberto_fabricante",
                    "collection_method": "download_oficial_catalogo",
                    "collected_at": now,
                    "audited_by": "Ricardo (Compliance)",
                    "audit_id": "AUD-2026-0001",
                },
            },
        ),
        (
            "Padrão SAE J2012 — código DTC",
            {
                "content": "P0301: falha de combustão detectada no cilindro 1 (misfire).",
                "content_class": "codigo_dtc_sae_iso",
                "vehicle_make": "Genérico",
                "vehicle_model": "OBD-II",
                "provenance": {
                    "source_type": "padrao_sae_iso",
                    "source_name": "SAE J2012 — definições de DTC",
                    "standard_ref": "SAE J2012",
                    "license_basis": "referencia_factual_padrao",
                    "collection_method": "digitacao_manual_auditada",
                    "collected_at": now,
                    "audited_by": "Ricardo (Compliance)",
                    "audit_id": "AUD-2026-0002",
                },
            },
        ),
        (
            "Telemetria interna — torque medido em O.S. anonimizada",
            {
                "content": "Cabeçote 1.0 8V: reaperto final medido em oficina, 38 Nm após aquecimento.",
                "content_class": "torque_nm",
                "vehicle_make": "Fiat",
                "vehicle_model": "Uno Mille",
                "provenance": {
                    "source_type": "telemetria_interna",
                    "source_name": "Ordens de Serviço Zezé da Regulagem",
                    "license_basis": "dado_proprio_titularidade_interna",
                    "collection_method": "exportacao_ordem_servico",
                    "collected_at": now,
                    "audited_by": "Ricardo (Compliance)",
                    "audit_id": "AUD-2026-0003",
                    "tenant_id": tenant,
                    "lgpd_basis": "legitimo_interesse",
                    "pii_scrubbed": True,
                },
            },
        ),
        (
            "BLOQUEIO — scraping de base proprietária (Doutor-IE)",
            {
                "content": "Diagrama de injeção completo com passo a passo de reparo e valores.",
                "content_class": "especificacao_eletrica",
                "vehicle_make": "VW",
                "vehicle_model": "Gol G5",
                "provenance": {
                    "source_type": "catalogo_aberto",
                    "source_name": "Doutor-IE",
                    "source_uri": "https://www.doutor-ie.com.br/manual",  # nosemgrep: autotech.compliance-ip-blocked-proprietary-source
                    "license_basis": "catalogo_aberto_fabricante",
                    "collection_method": "web_scraping",
                    "collected_at": now,
                    "audited_by": "bot-crawler",
                    "audit_id": "AUD-2026-0004",
                },
            },
        ),
        (
            "BLOQUEIO — telemetria com dado pessoal (placa e CPF)",
            {
                "content": "Cliente CPF 123.456.789-09, placa ABC1D23, torque 90 Nm na roda.",
                "content_class": "torque_nm",
                "vehicle_make": "Chevrolet",
                "vehicle_model": "Onix",
                "provenance": {
                    "source_type": "telemetria_interna",
                    "source_name": "Ordens de Serviço Zezé da Regulagem",
                    "license_basis": "dado_proprio_titularidade_interna",
                    "collection_method": "exportacao_ordem_servico",
                    "collected_at": now,
                    "audited_by": "Ricardo (Compliance)",
                    "audit_id": "AUD-2026-0005",
                    "tenant_id": tenant,
                    "lgpd_basis": "execucao_de_contrato",
                    "pii_scrubbed": True,
                },
            },
        ),
        (
            "BLOQUEIO — trecho de manual com copyright",
            {
                "content": "© 2024 Editora Técnica. Todos os direitos reservados. Torque 25 Nm.",
                "content_class": "torque_nm",
                "vehicle_make": "Ford",
                "vehicle_model": "Ka",
                "provenance": {
                    "source_type": "padrao_sae_iso",
                    "source_name": "Manual de editora técnica",
                    "standard_ref": "ISO 15031-6",
                    "license_basis": "referencia_factual_padrao",
                    "collection_method": "digitacao_manual_auditada",
                    "collected_at": now,
                    "audited_by": "Ricardo (Compliance)",
                    "audit_id": "AUD-2026-0006",
                },
            },
        ),
    ]


def main() -> int:
    """Executa a demonstração do gate e devolve 0 se o comportamento esperado ocorrer."""
    expected_accept = (True, True, True, False, False, False)
    outcomes: list[bool] = []
    sys.stdout.write("=== Gate de Ingestão RAG — Compliance as Code (LGPD / Lei 9.610/98) ===\n")
    for title, raw in _demo_records():
        chunk, decision = admit(raw)
        outcomes.append(decision.accepted)
        status = "ACEITO   " if decision.accepted else "REJEITADO"
        sys.stdout.write(f"\n[{status}] {title}\n")
        if chunk is not None:
            with_vector = chunk.model_copy(
                update={"embedding": deterministic_demo_embedding(chunk.content)}
            )
            row = with_vector.to_pgvector_row()
            sys.stdout.write(f"    fingerprint : {decision.fingerprint}\n")
            sys.stdout.write(
                f"    auditoria   : {decision.audit_id} | licença: {row['license_basis']}\n"
            )
            sys.stdout.write(f"    vetor       : {EMBEDDING_DIM} dimensões -> pgvector\n")
        for reason in decision.reasons:
            sys.stdout.write(f"    motivo      : {reason}\n")
    sys.stdout.write("\nSQL parametrizado de persistência:\n  " + INSERT_CHUNK_SQL + "\n")
    summary = {"aceitos": outcomes.count(True), "rejeitados": outcomes.count(False)}
    sys.stdout.write("Resumo: " + json.dumps(summary) + "\n")
    return 0 if tuple(outcomes) == expected_accept else 1


if __name__ == "__main__":
    sys.exit(main())
