"""Roche Cobas Integra 400/800 — bioquímica; usa ASTM E1394.
"""
from app.modules.mrinterface.drivers.generic_astm import GenericASTMDriver


class RocheCobasIntegraDriver(GenericASTMDriver):
    code = "roche_cobas_integra"
    vendor = "Roche"
    model = "Cobas Integra 400/800"
    section = "bioquimica"
    default_protocol = "astm_tcp"
