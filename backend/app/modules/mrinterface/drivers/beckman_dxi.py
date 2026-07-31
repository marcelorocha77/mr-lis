"""Beckman Coulter Access DxI / UniCel DxI 600/800 — imunoensaio.
Protocolo: HL7 v2.
"""
from app.modules.mrinterface.drivers.generic_hl7 import GenericHL7Driver


class BeckmanDxIDriver(GenericHL7Driver):
    code = "beckman_dxi"
    vendor = "Beckman Coulter"
    model = "Access DxI"
    section = "hormonios"
    default_protocol = "hl7_mllp"
