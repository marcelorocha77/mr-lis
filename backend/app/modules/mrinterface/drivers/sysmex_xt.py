"""Sysmex XT-series (XT-1800i, XT-2000i, XT-4000i) — hematologia.
Protocolo: ASTM E1394 sobre TCP (porta 4000 típica).
"""
from app.modules.mrinterface.drivers.generic_astm import GenericASTMDriver


class SysmexXTDriver(GenericASTMDriver):
    code = "sysmex_xt"
    vendor = "Sysmex"
    model = "XT-series"
    section = "hematologia"
    default_protocol = "astm_tcp"
