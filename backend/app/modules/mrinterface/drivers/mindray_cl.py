"""Mindray CL-series (CL-900i, CL-1200i, CL-2000i, CL-6000i) — imunoensaio quimioluminescente.
Protocolo: HL7 v2.
"""
from app.modules.mrinterface.drivers.generic_hl7 import GenericHL7Driver


class MindrayCLDriver(GenericHL7Driver):
    code = "mindray_cl"
    vendor = "Mindray"
    model = "CL-series"
    section = "hormonios"
    default_protocol = "hl7_mllp"
