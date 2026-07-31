"""Abbott Architect i-series (i1000SR, i2000, i2000SR) — imunoensaio.
Protocolo: ASTM E1394 sobre TCP.
"""
from app.modules.mrinterface.drivers.generic_astm import GenericASTMDriver


class AbbottArchitectIDriver(GenericASTMDriver):
    code = "abbott_architect_i"
    vendor = "Abbott"
    model = "Architect i-series"
    section = "hormonios"
    default_protocol = "astm_tcp"
