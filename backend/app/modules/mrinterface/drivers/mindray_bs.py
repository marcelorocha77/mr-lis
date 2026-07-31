"""Mindray BS-series (BS-240, BS-380, BS-480, BS-600, BS-800M) — bioquímica.
Protocolo: HL7 v2 (versões novas) ou ASTM (legado).
"""
from app.modules.mrinterface.drivers.generic_hl7 import GenericHL7Driver


class MindrayBSDriver(GenericHL7Driver):
    code = "mindray_bs"
    vendor = "Mindray"
    model = "BS-series"
    section = "bioquimica"
    default_protocol = "hl7_mllp"
