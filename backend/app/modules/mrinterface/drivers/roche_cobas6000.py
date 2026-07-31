"""Roche Cobas 6000 — bioquímica + imunologia (c501 + e601 integrados).
Protocolo: HL7 v2.5 sobre MLLP TCP, porta 5000 típica.
"""
from app.modules.mrinterface.drivers.generic_hl7 import GenericHL7Driver


class RocheCobas6000Driver(GenericHL7Driver):
    code = "roche_cobas6000"
    vendor = "Roche"
    model = "Cobas 6000"
    section = "bioquimica"
    default_protocol = "hl7_mllp"
