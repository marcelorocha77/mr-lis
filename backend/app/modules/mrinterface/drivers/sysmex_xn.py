"""Sysmex XN-series (XN-550, XN-1000, XN-2000, XN-3000, XN-9000) — hematologia.
Protocolo: HL7 v2.3.1 sobre MLLP TCP.
"""
from app.modules.mrinterface.drivers.generic_hl7 import GenericHL7Driver


class SysmexXNDriver(GenericHL7Driver):
    code = "sysmex_xn"
    vendor = "Sysmex"
    model = "XN-series"
    section = "hematologia"
    default_protocol = "hl7_mllp"
