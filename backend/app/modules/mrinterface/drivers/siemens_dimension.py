"""Siemens Dimension EXL 200 / RxL Max / Xpand — bioquímica.
Protocolo: ASTM E1394.
"""
from app.modules.mrinterface.drivers.generic_astm import GenericASTMDriver


class SiemensDimensionDriver(GenericASTMDriver):
    code = "siemens_dimension"
    vendor = "Siemens"
    model = "Dimension EXL/RxL/Xpand"
    section = "bioquimica"
    default_protocol = "astm_tcp"
