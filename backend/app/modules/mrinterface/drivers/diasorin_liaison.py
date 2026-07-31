"""DiaSorin Liaison XL / XS — imunoensaio.
Protocolo: HL7 v2 sobre MLLP.
"""
from app.modules.mrinterface.drivers.generic_hl7 import GenericHL7Driver


class DiaSorinLiaisonDriver(GenericHL7Driver):
    code = "diasorin_liaison"
    vendor = "DiaSorin"
    model = "Liaison XL/XS"
    section = "hormonios"
    default_protocol = "hl7_mllp"
