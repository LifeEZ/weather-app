"""initial

Revision ID: 0001
Revises:
Create Date: 2026-05-19
"""
import sqlalchemy as sa
from alembic import op

revision = "1d22dc3d6e9a"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "weather_queries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("city", sa.String(), nullable=False),
        sa.Column("temperature", sa.Float(), nullable=False),
        sa.Column("feels_like", sa.Float(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("humidity", sa.Integer(), nullable=False),
        sa.Column("wind_speed", sa.Float(), nullable=False),
        sa.Column("queried_at", sa.DateTime(), nullable=False),
        sa.Column("from_cache", sa.Boolean(), nullable=False),
        sa.Column("unit", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_weather_queries_id"), "weather_queries", ["id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_weather_queries_id"), table_name="weather_queries")
    op.drop_table("weather_queries")
