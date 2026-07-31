"""Abbott Architect c-series (c4000, c8000, c16000) — bioquímica.
Protocolo: ASTM E1394 sobre TCP.
"""
from app.modules.mrinterface.drivers.generic_astm import GenericASTMDriver


class AbbottArchitectCDriver(GenericASTMDriver):
    code = "abbott_architect_c"
    vendor = "Abbott"
    model = "Architect c-series"
    section = "bioquimica"
    default_protocol = "astm_tcp"
