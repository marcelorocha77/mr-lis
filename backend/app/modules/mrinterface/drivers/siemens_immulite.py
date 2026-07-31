"""Siemens Immulite 1000 / 2000 / 2500 / XPI — imunoensaio.
Protocolo: ASTM sobre serial ou TCP.
"""
from app.modules.mrinterface.drivers.generic_astm import GenericASTMDriver


class SiemensImmuliteDriver(GenericASTMDriver):
    code = "siemens_immulite"
    vendor = "Siemens"
    model = "Immulite 1000/2000/2500"
    section = "hormonios"
    default_protocol = "astm_serial"
