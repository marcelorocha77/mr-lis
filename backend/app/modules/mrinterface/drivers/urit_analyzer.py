"""URIT (BH-5390, BH-3200, hematologia + urinálise).
Protocolo: ASTM ou serial.
"""
from app.modules.mrinterface.drivers.generic_astm import GenericASTMDriver


class UritAnalyzerDriver(GenericASTMDriver):
    code = "urit_analyzer"
    vendor = "URIT"
    model = "BH-series / urinalise"
    section = "hematologia"
    default_protocol = "astm_tcp"
