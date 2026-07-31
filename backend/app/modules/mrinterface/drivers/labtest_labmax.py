"""Labtest LabMax 240 / 560 / Progress — bioquímica (fabricante brasileiro).
Protocolo: ASTM, também aceita arquivo.
"""
from app.modules.mrinterface.drivers.generic_astm import GenericASTMDriver


class LabtestLabMaxDriver(GenericASTMDriver):
    code = "labtest_labmax"
    vendor = "Labtest"
    model = "LabMax 240 / 560 / Progress"
    section = "bioquimica"
    default_protocol = "astm_serial"
