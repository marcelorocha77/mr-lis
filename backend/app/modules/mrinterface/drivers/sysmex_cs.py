"""Sysmex CS-series (CS-2000i, CS-2500, CS-5100) — coagulação.
Protocolo: HL7 v2.
"""
from app.modules.mrinterface.drivers.generic_hl7 import GenericHL7Driver


class SysmexCSDriver(GenericHL7Driver):
    code = "sysmex_cs"
    vendor = "Sysmex"
    model = "CS-series (Coag)"
    section = "coagulacao"
    default_protocol = "hl7_mllp"
