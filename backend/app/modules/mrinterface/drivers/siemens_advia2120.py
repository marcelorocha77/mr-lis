"""Siemens Advia 2120 / 2120i — hematologia.
Protocolo: ASTM (também suporta arquivo).
"""
from app.modules.mrinterface.drivers.generic_astm import GenericASTMDriver


class SiemensAdvia2120Driver(GenericASTMDriver):
    code = "siemens_advia2120"
    vendor = "Siemens"
    model = "Advia 2120"
    section = "hematologia"
    default_protocol = "astm_tcp"
