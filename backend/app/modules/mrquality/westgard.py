"""Motor de regras Westgard e cálculos estatísticos de QC.

Regras suportadas:
- 1_2s: uma medida > ±2 SD (aviso; não rejeita)
- 1_3s: uma medida > ±3 SD (rejeição)
- 2_2s: duas medidas consecutivas > +2 SD (ou < -2 SD) (rejeição)
- R_4s: range entre duas medidas consecutivas > 4 SD (rejeição)
- 4_1s: quatro medidas consecutivas > +1 SD (ou < -1 SD) (rejeição)
- 10x:  dez medidas consecutivas do mesmo lado da média (rejeição)
- 8x:   oito consecutivas do mesmo lado (variante)
- 12x:  doze consecutivas do mesmo lado (variante)
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from statistics import mean, stdev


ALL_RULES = [
    ("1_2s", "Uma medida além de ±2 SD", "warning"),
    ("1_3s", "Uma medida além de ±3 SD", "rejection"),
    ("2_2s", "Duas medidas consecutivas além de +2 SD (ou -2 SD)", "rejection"),
    ("R_4s", "Diferença entre duas medidas consecutivas > 4 SD", "rejection"),
    ("4_1s", "Quatro medidas consecutivas além de +1 SD (ou -1 SD)", "rejection"),
    ("10x",  "Dez medidas consecutivas do mesmo lado da média", "rejection"),
    ("8x",   "Oito medidas consecutivas do mesmo lado da média", "rejection"),
    ("12x",  "Doze medidas consecutivas do mesmo lado da média", "rejection"),
]


@dataclass
class WestgardViolation:
    rule_code: str
    severity: str  # warning | rejection


def z_score(value: float, mean_v: float, sd: float) -> float:
    if sd == 0:
        return 0.0
    return (value - mean_v) / sd


def evaluate(
    values: list[float],   # do mais antigo para o mais novo, incluindo o valor atual como último
    mean_v: float,
    sd: float,
    active_rules: list[str] | None = None,
) -> list[WestgardViolation]:
    """Aplica cada regra sobre a série 'values' e retorna as violações detectadas
    para o ÚLTIMO ponto (o recém-inserido).
    """
    if sd <= 0 or not values:
        return []

    rules = set(active_rules or [r[0] for r in ALL_RULES])
    zs = [z_score(v, mean_v, sd) for v in values]
    last = zs[-1]
    violations: list[WestgardViolation] = []

    # 1_2s
    if "1_2s" in rules and abs(last) > 2:
        violations.append(WestgardViolation("1_2s", "warning"))

    # 1_3s
    if "1_3s" in rules and abs(last) > 3:
        violations.append(WestgardViolation("1_3s", "rejection"))

    # 2_2s — últimos 2 do mesmo lado, ambos além de 2 SD
    if "2_2s" in rules and len(zs) >= 2:
        z2 = zs[-2:]
        if all(z > 2 for z in z2) or all(z < -2 for z in z2):
            violations.append(WestgardViolation("2_2s", "rejection"))

    # R_4s — range entre 2 últimos > 4 SD
    if "R_4s" in rules and len(zs) >= 2:
        if abs(zs[-1] - zs[-2]) > 4:
            violations.append(WestgardViolation("R_4s", "rejection"))

    # 4_1s — últimos 4 do mesmo lado além de 1 SD
    if "4_1s" in rules and len(zs) >= 4:
        z4 = zs[-4:]
        if all(z > 1 for z in z4) or all(z < -1 for z in z4):
            violations.append(WestgardViolation("4_1s", "rejection"))

    # Nx (Nx do mesmo lado da média)
    for rule, n in (("10x", 10), ("8x", 8), ("12x", 12)):
        if rule in rules and len(zs) >= n:
            zn = zs[-n:]
            if all(z > 0 for z in zn) or all(z < 0 for z in zn):
                violations.append(WestgardViolation(rule, "rejection"))

    return violations


def sigma_metric(cv_percent: float, bias_percent: float, tea_percent: float) -> float:
    """Sigma metric de Westgard: σ = (TEa - |Bias|) / CV.
    Convenção: mundo-classe ≥6, aceitável ≥4, ruim <3.
    """
    if cv_percent <= 0:
        return 0.0
    return (tea_percent - abs(bias_percent)) / cv_percent


def moving_average(values: list[float], window: int = 5) -> list[float]:
    if not values or window < 1:
        return []
    out: list[float] = []
    for i in range(len(values)):
        start = max(0, i - window + 1)
        window_slice = values[start : i + 1]
        out.append(sum(window_slice) / len(window_slice))
    return out


def stats_summary(values: list[float]) -> dict:
    """Estatísticas resumo — média, SD, CV%, min, max, n."""
    if not values:
        return {"n": 0, "mean": 0.0, "sd": 0.0, "cv": 0.0, "min": 0.0, "max": 0.0}
    m = mean(values)
    sd = stdev(values) if len(values) > 1 else 0.0
    cv = (sd / m * 100) if m else 0.0
    return {
        "n": len(values),
        "mean": m,
        "sd": sd,
        "cv": cv,
        "min": min(values),
        "max": max(values),
    }


def total_error(bias_percent: float, cv_percent: float, k: float = 1.65) -> float:
    """TE = |Bias| + k*CV  (k=1.65 pra 95% de confiança unilateral)."""
    return abs(bias_percent) + k * cv_percent
