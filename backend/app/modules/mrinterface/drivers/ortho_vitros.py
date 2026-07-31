"""Ortho Clinical Diagnostics Vitros (350, 5600, 7600, XT 7600).
Protocolo: ASTM E1394 ou HL7 (série nova).
"""
from app.modules.mrinterface.drivers.generic_astm import GenericASTMDriver


class OrthoVitrosDriver(GenericASTMDriver):
    code = "ortho_vitros"
    vendor = "Ortho Clinical"
    model = "Vitros 5600/7600/XT 7600"
    section = "bioquimica"
    default_protocol = "astm_tcp"
