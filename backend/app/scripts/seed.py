"""Seed inicial: tenant demo + admin + exames + convênios básicos.

Rodar dentro do container:
    docker compose exec backend python -m app.scripts.seed
"""
import asyncio
from decimal import Decimal

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.exam import Exam
from app.models.insurance import Insurance
from app.models.tenant import Tenant
from app.models.user import User


from app.scripts.exam_catalog import EXAMS as DEMO_EXAMS


DEMO_INSURANCES = [
    ("PART", "Particular", None, "AMB"),
    ("UNI",  "Unimed", "379301", "TUSS"),
    ("BRAD", "Bradesco Saúde", "005711", "TUSS"),
    ("SULA", "SulAmérica Saúde", "006246", "TUSS"),
    ("AMIL", "Amil", "326305", "TUSS"),
    ("SUS",  "SUS", None, "SIGTAP"),
]


DEMO_EQUIPMENTS = [
    # code, name, driver, protocol, connection, section
    ("EQ001", "Cobas 6000 (Roche)",           "roche_cobas6000",    "hl7_mllp", {"bind": "0.0.0.0", "port": 5001}, "bioquimica"),
    ("EQ002", "XN-1000 (Sysmex)",             "sysmex_xn",          "hl7_mllp", {"bind": "0.0.0.0", "port": 5002}, "hematologia"),
    ("EQ003", "Architect ci4100 (Abbott)",    "abbott_architect_c", "astm_tcp", {"host": "10.0.1.50", "port": 4001}, "bioquimica"),
    ("EQ004", "Advia 2120 (Siemens)",         "siemens_advia2120",  "astm_tcp", {"host": "10.0.1.51", "port": 4002}, "hematologia"),
    ("EQ005", "Immulite 2000 (Siemens)",      "siemens_immulite",   "astm_serial", {"serial_port": "COM3", "baud": 9600}, "hormonios"),
    ("EQ006", "LabMax Progress (Labtest)",    "labtest_labmax",     "file", {"watch_dir": "/data/labmax_in", "pattern": "*.csv", "done_dir": "/data/labmax_done"}, "bioquimica"),
]


async def main():
    async with AsyncSessionLocal() as db:
        existing = await db.scalar(select(Tenant).where(Tenant.slug == "demo"))
        if existing:
            print("Seed already present.")
            return

        tenant = Tenant(slug="demo", name="Laboratório Demo", plan="pro", is_active=True)
        db.add(tenant)
        await db.flush()

        admin = User(
            tenant_id=tenant.id,
            email="admin@demo.mr",
            full_name="Administrador Demo",
            hashed_password=hash_password("mr123"),
            role="admin",
            is_active=True,
        )
        db.add(admin)

        for code, name, section, material, method, unit, tat, price in DEMO_EXAMS:
            db.add(Exam(
                tenant_id=tenant.id, code=code, name=name, section=section,
                material=material, method=method, unit=unit,
                turnaround_hours=tat, price=Decimal(price),
            ))

        for code, name, ans, table in DEMO_INSURANCES:
            db.add(Insurance(
                tenant_id=tenant.id, code=code, name=name,
                ans_code=ans, price_table=table,
            ))

        from app.models.equipment import Equipment
        for code, name, driver, protocol, conn, section in DEMO_EQUIPMENTS:
            db.add(Equipment(
                tenant_id=tenant.id, code=code, name=name,
                driver=driver, protocol=protocol, connection=conn, section=section,
                is_enabled=False,  # começa desativado; usuário ativa quando o hardware estiver lá
            ))

        await db.commit()
        print("Seed OK. Login: admin@demo.mr / mr123 (tenant: demo)")


if __name__ == "__main__":
    asyncio.run(main())
