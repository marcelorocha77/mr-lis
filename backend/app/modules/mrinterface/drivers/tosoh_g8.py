"""Tosoh G8 / G11 — HbA1c por HPLC.
Protocolo: ASTM.
"""
from app.modules.mrinterface.drivers.generic_astm import GenericASTMDriver


class TosohG8Driver(GenericASTMDriver):
    code = "tosoh_g8"
    vendor = "Tosoh"
    model = "G8 / G11 (HbA1c)"
    section = "bioquimica"
    default_protocol = "astm_serial"
