"""Driver genérico ASTM E1381/E1394 — base para equipamentos legados."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation

from app.modules.mrinterface.drivers.base import BaseDriver, DriverResult
from app.modules.mrinterface.protocols.astm import parse_records


def _to_decimal(v: str) -> Decimal | None:
    if not v:
        return None
    try:
        return Decimal(v.replace(",", "."))
    except (InvalidOperation, ValueError):
        return None


class GenericASTMDriver(BaseDriver):
    code = "generic_astm"
    vendor = "Generic"
    model = "ASTM E1394 (any analyzer)"
    section = ""
    default_protocol = "astm_tcp"

    def parse_message(self, payload: str) -> list[DriverResult]:
        results: list[DriverResult] = []
        current_request = ""
        for rec in parse_records(payload):
            if rec.type == "O":              # Order record — request_number no campo 3
                current_request = rec.field_at(2) or current_request
            elif rec.type == "R":            # Result record
                # R|seq|test_id|value|units|reference|flag|status|...
                test_id = rec.field_at(2)   # "^^^GLU"
                exam_code = test_id.split("^")[-1] if test_id else ""
                value = rec.field_at(3)
                unit = rec.field_at(4)
                ref = rec.field_at(5)
                flag = rec.field_at(6)
                num = _to_decimal(value)
                results.append(
                    DriverResult(
                        request_number=current_request,
                        exam_code=exam_code,
                        numeric_value=num,
                        text_value=value if num is None else None,
                        unit=unit or None,
                        flag=flag or None,
                        extras={"reference": ref} if ref else {},
                    )
                )
        return results
