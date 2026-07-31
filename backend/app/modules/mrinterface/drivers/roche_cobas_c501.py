"""Roche Cobas c501 — módulo de bioquímica avulso. HL7 MLLP."""
from app.modules.mrinterface.drivers.generic_hl7 import GenericHL7Driver


class RocheCobasC501Driver(GenericHL7Driver):
    code = "roche_cobas_c501"
    vendor = "Roche"
    model = "Cobas c501"
    section = "bioquimica"
    default_protocol = "hl7_mllp"
