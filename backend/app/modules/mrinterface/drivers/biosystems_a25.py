"""BioSystems A25 / A15 — bioquímica.
Protocolo: ASTM sobre serial.
"""
from app.modules.mrinterface.drivers.generic_astm import GenericASTMDriver


class BioSystemsA25Driver(GenericASTMDriver):
    code = "biosystems_a25"
    vendor = "BioSystems"
    model = "A25 / A15"
    section = "bioquimica"
    default_protocol = "astm_serial"
