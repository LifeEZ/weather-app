"""add indexes on city and queried_at

Revision ID: f3294cb45b62
Revises: 1d22dc3d6e9a
Create Date: 2026-05-19
"""
from alembic import op

revision = "f3294cb45b62"
down_revision = "1d22dc3d6e9a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_weather_queries_id", table_name="weather_queries")
    op.create_index(
        op.f("ix_weather_queries_city"),
        "weather_queries",
        ["city"],
        unique=False,
    )
    op.create_index(
        op.f("ix_weather_queries_queried_at"),
        "weather_queries",
        ["queried_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_weather_queries_queried_at"), table_name="weather_queries"
    )
    op.drop_index(
        op.f("ix_weather_queries_city"), table_name="weather_queries"
    )
    op.create_index(
        "ix_weather_queries_id", "weather_queries", ["id"], unique=False
    )
