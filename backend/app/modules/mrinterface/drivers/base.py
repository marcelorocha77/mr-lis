"""Classe base para todos os drivers de equipamento."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from typing import ClassVar


DRIVER_REGISTRY: dict[str, type["BaseDriver"]] = {}


@dataclass
class DriverResult:
    """Resultado extraído de uma mensagem do equipamento."""
    request_number: str
    exam_code: str
    numeric_value: Decimal | None = None
    text_value: str | None = None
    unit: str | None = None
    flag: str | None = None  # N, H, L, HH, LL, A
    method: str | None = None
    equipment: str | None = None
    extras: dict = field(default_factory=dict)


class BaseDriver(ABC):
    """Contrato de um driver de equipamento.

    Cada driver deve:
    - definir metadados de classe (vendor/model/section/default_protocol)
    - implementar parse_message() para transformar payload cru em list[DriverResult]
    - implementar build_order() para enviar uma requisição ao equipamento (host-query / ORM)
    """

    # metadados obrigatórios
    code: ClassVar[str] = ""              # snake_case slug — vendor_model
    vendor: ClassVar[str] = ""
    model: ClassVar[str] = ""
    section: ClassVar[str] = ""
    default_protocol: ClassVar[str] = "hl7_mllp"

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.code:
            DRIVER_REGISTRY[cls.code] = cls

    def __init__(self, connection: dict):
        self.connection = connection

    @abstractmethod
    def parse_message(self, payload: str) -> list[DriverResult]:
        """Transforma payload cru em resultados estruturados."""

    def build_order(self, request_number: str, exam_codes: list[str]) -> str | None:
        """Constrói mensagem de ordem/host-query para enviar ao equipamento.

        Alguns equipamentos são apenas outbound (só enviam resultados) — nesse caso,
        retorna None e o driver não gera ordens.
        """
        return None

    def build_ack(self, payload: str) -> str | None:
        """Constrói mensagem de reconhecimento (ACK) para o payload recebido.

        Para HL7, gera um MSH/MSA. Para ASTM, o protocolo já faz ACK byte-a-byte
        no protocol handler.
        """
        return None
