"""Siemens Atellica Solution — plataforma integrada (CH + IM + CI).
Protocolo: HL7 v2.
"""
from app.modules.mrinterface.drivers.generic_hl7 import GenericHL7Driver


class SiemensAtellicaDriver(GenericHL7Driver):
    code = "siemens_atellica"
    vendor = "Siemens"
    model = "Atellica"
    section = "bioquimica"
    default_protocol = "hl7_mllp"
