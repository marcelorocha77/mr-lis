"""Beckman AU 480 / 680 / 400 — bioquímica.
Protocolo: ASTM E1394 sobre serial ou TCP.
"""
from app.modules.mrinterface.drivers.generic_astm import GenericASTMDriver


class BeckmanAU680Driver(GenericASTMDriver):
    code = "beckman_au680"
    vendor = "Beckman Coulter"
    model = "AU 480/680"
    section = "bioquimica"
    default_protocol = "astm_tcp"
