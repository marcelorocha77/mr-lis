"""Beckman Coulter DxH 800 / 900 — hematologia.
Protocolo: HL7 v2 sobre MLLP.
"""
from app.modules.mrinterface.drivers.generic_hl7 import GenericHL7Driver


class BeckmanDxHDriver(GenericHL7Driver):
    code = "beckman_dxh"
    vendor = "Beckman Coulter"
    model = "DxH 800/900"
    section = "hematologia"
    default_protocol = "hl7_mllp"
