"""Alifax Test 1 / Roller 20 — VHS automatizado.
Protocolo: ASTM.
"""
from app.modules.mrinterface.drivers.generic_astm import GenericASTMDriver


class AlifaxTest1Driver(GenericASTMDriver):
    code = "alifax_test1"
    vendor = "Alifax"
    model = "Test 1 / Roller"
    section = "hematologia"
    default_protocol = "astm_tcp"
