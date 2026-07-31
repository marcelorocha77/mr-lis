"""Roche Cobas e601 — módulo de imunoensaio (Elecsys) avulso. HL7 MLLP."""
from app.modules.mrinterface.drivers.generic_hl7 import GenericHL7Driver


class RocheCobasE601Driver(GenericHL7Driver):
    code = "roche_cobas_e601"
    vendor = "Roche"
    model = "Cobas e601"
    section = "hormonios"
    default_protocol = "hl7_mllp"
