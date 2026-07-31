"""Registry central de drivers de equipamento.

Cada driver herda de BaseDriver e se registra automaticamente ao ser importado.
"""
from app.modules.mrinterface.drivers.base import BaseDriver, DriverResult, DRIVER_REGISTRY

# importar todos os drivers para popular o registry
from app.modules.mrinterface.drivers import (  # noqa: F401
    generic_hl7,
    generic_astm,
    generic_file,
    roche_cobas6000,
    roche_cobas8000,
    roche_cobas_integra,
    roche_cobas_c501,
    roche_cobas_e601,
    sysmex_xn,
    sysmex_xt,
    sysmex_cs,
    abbott_architect_c,
    abbott_architect_i,
    siemens_advia2120,
    siemens_advia560,
    siemens_dimension,
    siemens_centaur,
    siemens_immulite,
    siemens_atellica,
    beckman_dxh,
    beckman_dxi,
    beckman_au680,
    beckman_au5800,
    ortho_vitros,
    mindray_bs,
    mindray_cl,
    mindray_bc,
    snibe_maglumi,
    alifax_test1,
    diasorin_liaison,
    tosoh_g8,
    urit_analyzer,
    biosystems_a25,
    labtest_labmax,
)


def list_drivers() -> list[dict]:
    return [
        {
            "code": name,
            "vendor": cls.vendor,
            "model": cls.model,
            "protocol": cls.default_protocol,
            "section": cls.section,
        }
        for name, cls in sorted(DRIVER_REGISTRY.items())
    ]


def get_driver(name: str) -> type[BaseDriver] | None:
    return DRIVER_REGISTRY.get(name)


__all__ = ["BaseDriver", "DriverResult", "list_drivers", "get_driver", "DRIVER_REGISTRY"]
