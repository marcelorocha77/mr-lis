"""Snibe Maglumi (600, 800, 1000, 2000, 3000, 4000, X3, X8) — imunoensaio CLIA.
Protocolo: ASTM E1394 ou HL7 (versão nova).
"""
from app.modules.mrinterface.drivers.generic_astm import GenericASTMDriver


class SnibeMaglumiDriver(GenericASTMDriver):
    code = "snibe_maglumi"
    vendor = "Snibe"
    model = "Maglumi"
    section = "hormonios"
    default_protocol = "astm_tcp"
