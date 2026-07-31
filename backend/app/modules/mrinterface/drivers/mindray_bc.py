"""Mindray BC-series (BC-3000, BC-5150, BC-5380, BC-6800) — hematologia.
Protocolo: HL7 ou ASTM.
"""
from app.modules.mrinterface.drivers.generic_hl7 import GenericHL7Driver


class MindrayBCDriver(GenericHL7Driver):
    code = "mindray_bc"
    vendor = "Mindray"
    model = "BC-series (hemato)"
    section = "hematologia"
    default_protocol = "hl7_mllp"
