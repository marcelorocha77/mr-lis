"""Driver genérico de arquivos — CSV/TXT deixado pelo equipamento numa pasta.

Formato esperado (CSV com header):
    request_number,exam_code,value,unit,flag
    R202607311230,GLU,102,mg/dL,N
    R202607311230,CREA,0.9,mg/dL,N
"""
from __future__ import annotations

import csv
import io
from decimal import Decimal, InvalidOperation

from app.modules.mrinterface.drivers.base import BaseDriver, DriverResult


class GenericFileDriver(BaseDriver):
    code = "generic_file"
    vendor = "Generic"
    model = "CSV / TXT file drop"
    section = ""
    default_protocol = "file"

    def parse_message(self, payload: str) -> list[DriverResult]:
        results: list[DriverResult] = []
        reader = csv.DictReader(io.StringIO(payload))
        for row in reader:
            try:
                num = Decimal(str(row.get("value", "")).replace(",", "."))
            except (InvalidOperation, ValueError):
                num = None
            results.append(
                DriverResult(
                    request_number=row.get("request_number", ""),
                    exam_code=row.get("exam_code", ""),
                    numeric_value=num,
                    text_value=row.get("value") if num is None else None,
                    unit=row.get("unit") or None,
                    flag=row.get("flag") or None,
                )
            )
        return results
