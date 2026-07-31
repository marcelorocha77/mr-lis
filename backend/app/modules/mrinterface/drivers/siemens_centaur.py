"""Siemens Advia Centaur XP / XPT / CP — imunoensaio.
Protocolo: LIS02-A2 (ASTM).
"""
from app.modules.mrinterface.drivers.generic_astm import GenericASTMDriver


class SiemensCentaurDriver(GenericASTMDriver):
    code = "siemens_centaur"
    vendor = "Siemens"
    model = "Advia Centaur"
    section = "hormonios"
    default_protocol = "astm_tcp"
