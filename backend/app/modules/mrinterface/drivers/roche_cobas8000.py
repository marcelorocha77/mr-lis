"""Roche Cobas 8000 — bioquímica + imunologia de alto volume (c701/c702/e801).
Protocolo: HL7 v2.5 sobre MLLP.
"""
from app.modules.mrinterface.drivers.generic_hl7 import GenericHL7Driver


class RocheCobas8000Driver(GenericHL7Driver):
    code = "roche_cobas8000"
    vendor = "Roche"
    model = "Cobas 8000"
    section = "bioquimica"
    default_protocol = "hl7_mllp"
