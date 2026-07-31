"""Driver genérico HL7 v2 — usado como base para a maioria dos equipamentos modernos.

Espera mensagens ORU^R01 (observation result) via MLLP TCP.
Cada OBX vira um DriverResult. O request_number é lido do OBR-3 (Filler Order Number)
ou do OBR-2 (Placer Order Number), o que estiver preenchido primeiro.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation

from app.modules.mrinterface.drivers.base import BaseDriver, DriverResult
from app.modules.mrinterface.protocols.hl7_mllp import build_ack, parse_hl7


def _to_decimal(v: str) -> Decimal | None:
    if not v:
        return None
    try:
        return Decimal(v.replace(",", "."))
    except (InvalidOperation, ValueError):
        return None


class GenericHL7Driver(BaseDriver):
    code = "generic_hl7"
    vendor = "Generic"
    model = "HL7 v2 (any analyzer)"
    section = ""
    default_protocol = "hl7_mllp"

    def parse_message(self, payload: str) -> list[DriverResult]:
        results: list[DriverResult] = []
        segments = parse_hl7(payload)
        current_request = ""
        for seg in segments:
            if seg.name == "OBR":
                current_request = seg.field(3) or seg.field(2)
            elif seg.name == "OBX":
                obs_id = seg.field(3)          # ex: "GLU^Glucose^L"
                obs_value = seg.field(5)
                unit = seg.field(6)
                ref = seg.field(7)
                flag = seg.field(8)
                exam_code = obs_id.split("^")[0] if obs_id else ""
                num = _to_decimal(obs_value)
                results.append(
                    DriverResult(
                        request_number=current_request,
                        exam_code=exam_code,
                        numeric_value=num,
                        text_value=obs_value if num is None else None,
                        unit=unit or None,
                        flag=flag or None,
                        extras={"reference": ref} if ref else {},
                    )
                )
        return results

    def build_ack(self, payload: str) -> str | None:
        segments = parse_hl7(payload)
        if not segments or segments[0].name != "MSH":
            return None
        return build_ack(segments[0], "AA", "Message received")

    def build_order(self, request_number: str, exam_codes: list[str]) -> str:
        """Constrói ORM^O01 mínimo (host-query / worklist push)."""
        msh = "MSH|^~\\&|MR_LIS|LAB|EQP|LAB|20260101120000||ORM^O01|MSGID001|P|2.5"
        pid = f"PID|1||{request_number}"
        orc = f"ORC|NW|{request_number}"
        obrs = []
        for i, code in enumerate(exam_codes, start=1):
            obrs.append(f"OBR|{i}|{request_number}|{request_number}|{code}")
        return "\r".join([msh, pid, orc, *obrs])
