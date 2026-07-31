"""equipment + interface_messages

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-31

"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "equipments",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("driver", sa.String(60), nullable=False),
        sa.Column("protocol", sa.String(20), nullable=False, server_default="hl7_mllp"),
        sa.Column("connection", sa.JSON, nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("section", sa.String(60)),
        sa.Column("direction", sa.String(20), nullable=False, server_default="bidirectional"),
        sa.Column("is_enabled", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("last_seen", sa.DateTime(timezone=True)),
        sa.Column("last_error", sa.String(500)),
        sa.Column("pending_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "code", name="uq_equipments_tenant_code"),
    )
    op.create_index("ix_equipments_tenant_id", "equipments", ["tenant_id"])
    op.create_index("ix_equipments_code", "equipments", ["code"])

    op.create_table(
        "interface_messages",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("tenant_id", sa.Integer, sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("equipment_id", sa.Integer),
        sa.Column("direction", sa.String(10), nullable=False),
        sa.Column("protocol", sa.String(20), nullable=False),
        sa.Column("message_type", sa.String(20)),
        sa.Column("raw", sa.Text, nullable=False),
        sa.Column("parsed", sa.JSON),
        sa.Column("status", sa.String(20), nullable=False, server_default="ok"),
        sa.Column("request_number", sa.String(20)),
        sa.Column("error", sa.String(500)),
    )
    op.create_index("ix_interface_messages_tenant_id", "interface_messages", ["tenant_id"])
    op.create_index("ix_interface_messages_at", "interface_messages", ["at"])
    op.create_index("ix_interface_messages_equipment_id", "interface_messages", ["equipment_id"])
    op.create_index("ix_interface_messages_request_number", "interface_messages", ["request_number"])


def downgrade() -> None:
    op.drop_table("interface_messages")
    op.drop_table("equipments")
