"""Siemens Advia 560 — hematologia (5-part diff, entry level).
Protocolo: ASTM ou arquivo QRCode/CSV.
"""
from app.modules.mrinterface.drivers.generic_astm import GenericASTMDriver


class SiemensAdvia560Driver(GenericASTMDriver):
    code = "siemens_advia560"
    vendor = "Siemens"
    model = "Advia 560"
    section = "hematologia"
    default_protocol = "astm_tcp"
