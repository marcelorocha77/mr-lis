"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-31

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # tenants
    op.create_table(
        "tenants",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("slug", sa.String(60), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("cnpj", sa.String(20)),
        sa.Column("plan", sa.String(20), nullable=False, server_default="starter"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_tenants_slug", "tenants", ["slug"])

    # users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("email", sa.String(200), nullable=False),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(30), nullable=False, server_default="tecnico"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),
    )
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])
    op.create_index("ix_users_email", "users", ["email"])

    # patients
    op.create_table(
        "patients",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("cpf", sa.String(14)),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("social_name", sa.String(200)),
        sa.Column("birth_date", sa.Date),
        sa.Column("sex", sa.String(1)),
        sa.Column("phone", sa.String(20)),
        sa.Column("email", sa.String(200)),
        sa.Column("mother_name", sa.String(200)),
        sa.Column("address_street", sa.String(200)),
        sa.Column("address_number", sa.String(20)),
        sa.Column("address_complement", sa.String(100)),
        sa.Column("address_district", sa.String(100)),
        sa.Column("address_city", sa.String(100)),
        sa.Column("address_state", sa.String(2)),
        sa.Column("address_zip", sa.String(10)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "cpf", name="uq_patients_tenant_cpf"),
    )
    op.create_index("ix_patients_tenant_id", "patients", ["tenant_id"])
    op.create_index("ix_patients_full_name", "patients", ["full_name"])
    op.create_index("ix_patients_cpf", "patients", ["cpf"])

    # doctors
    op.create_table(
        "doctors",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("crm", sa.String(15), nullable=False),
        sa.Column("crm_uf", sa.String(2), nullable=False),
        sa.Column("specialty", sa.String(100)),
        sa.Column("phone", sa.String(20)),
        sa.Column("email", sa.String(200)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "crm", "crm_uf", name="uq_doctors_tenant_crm"),
    )
    op.create_index("ix_doctors_tenant_id", "doctors", ["tenant_id"])
    op.create_index("ix_doctors_full_name", "doctors", ["full_name"])
    op.create_index("ix_doctors_crm", "doctors", ["crm"])

    # insurances
    op.create_table(
        "insurances",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("ans_code", sa.String(20)),
        sa.Column("price_table", sa.String(30)),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "code", name="uq_insurances_tenant_code"),
    )
    op.create_index("ix_insurances_tenant_id", "insurances", ["tenant_id"])
    op.create_index("ix_insurances_code", "insurances", ["code"])

    # exams
    op.create_table(
        "exams",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("section", sa.String(60)),
        sa.Column("material", sa.String(60)),
        sa.Column("method", sa.String(120)),
        sa.Column("unit", sa.String(20)),
        sa.Column("turnaround_hours", sa.Integer, nullable=False, server_default="24"),
        sa.Column("price", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "code", name="uq_exams_tenant_code"),
    )
    op.create_index("ix_exams_tenant_id", "exams", ["tenant_id"])
    op.create_index("ix_exams_code", "exams", ["code"])

    # requests
    op.create_table(
        "requests",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("number", sa.String(20), nullable=False),
        sa.Column("patient_id", sa.Integer, sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("doctor_id", sa.Integer, sa.ForeignKey("doctors.id")),
        sa.Column("insurance_id", sa.Integer, sa.ForeignKey("insurances.id")),
        sa.Column("collection_datetime", sa.DateTime(timezone=True)),
        sa.Column("received_datetime", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("status", sa.String(20), nullable=False, server_default="aberta"),
        sa.Column("clinical_info", sa.String(2000)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_requests_tenant_id", "requests", ["tenant_id"])
    op.create_index("ix_requests_number", "requests", ["number"])
    op.create_index("ix_requests_patient_id", "requests", ["patient_id"])

    # request_items
    op.create_table(
        "request_items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("request_id", sa.Integer, sa.ForeignKey("requests.id"), nullable=False),
        sa.Column("exam_id", sa.Integer, sa.ForeignKey("exams.id"), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("status", sa.String(20), nullable=False, server_default="pendente"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_request_items_tenant_id", "request_items", ["tenant_id"])
    op.create_index("ix_request_items_request_id", "request_items", ["request_id"])

    # samples
    op.create_table(
        "samples",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("barcode", sa.String(40), nullable=False, unique=True),
        sa.Column("request_id", sa.Integer, sa.ForeignKey("requests.id"), nullable=False),
        sa.Column("material", sa.String(60), nullable=False),
        sa.Column("tube_type", sa.String(40)),
        sa.Column("collected_at", sa.DateTime(timezone=True)),
        sa.Column("received_at", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(20), nullable=False, server_default="pendente"),
        sa.Column("notes", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_samples_tenant_id", "samples", ["tenant_id"])
    op.create_index("ix_samples_barcode", "samples", ["barcode"])
    op.create_index("ix_samples_request_id", "samples", ["request_id"])

    # results
    op.create_table(
        "results",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("request_item_id", sa.Integer, sa.ForeignKey("request_items.id"), nullable=False, unique=True),
        sa.Column("numeric_value", sa.Numeric(18, 6)),
        sa.Column("text_value", sa.String(2000)),
        sa.Column("unit", sa.String(20)),
        sa.Column("reference_range", sa.String(120)),
        sa.Column("flag", sa.String(10)),
        sa.Column("method", sa.String(120)),
        sa.Column("equipment", sa.String(60)),
        sa.Column("entered_by_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("entered_at", sa.DateTime(timezone=True)),
        sa.Column("released_by_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("released_at", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(20), nullable=False, server_default="rascunho"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_results_tenant_id", "results", ["tenant_id"])

    # audit_logs
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("action", sa.String(60), nullable=False),
        sa.Column("entity", sa.String(60), nullable=False),
        sa.Column("entity_id", sa.String(40)),
        sa.Column("detail", sa.Text),
        sa.Column("ip", sa.String(45)),
    )
    op.create_index("ix_audit_logs_tenant_id", "audit_logs", ["tenant_id"])
    op.create_index("ix_audit_logs_at", "audit_logs", ["at"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])


def downgrade() -> None:
    for t in [
        "audit_logs", "results", "samples", "request_items", "requests",
        "exams", "insurances", "doctors", "patients", "users", "tenants",
    ]:
        op.drop_table(t)
