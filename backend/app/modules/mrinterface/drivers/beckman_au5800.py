"""Beckman AU 5800 — bioquímica de alto volume.
Protocolo: HL7 v2 (versão nova) ou ASTM (legado).
"""
from app.modules.mrinterface.drivers.generic_hl7 import GenericHL7Driver


class BeckmanAU5800Driver(GenericHL7Driver):
    code = "beckman_au5800"
    vendor = "Beckman Coulter"
    model = "AU 5800"
    section = "bioquimica"
    default_protocol = "hl7_mllp"
