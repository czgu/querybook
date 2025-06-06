"""add python cell

Revision ID: e7a17a8acf4c
Revises: d3582302cf48
Create Date: 2025-03-06 08:34:46.129355

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "e7a17a8acf4c"
down_revision = "d3582302cf48"
branch_labels = None
depends_on = None


# Define the old and new DataCellType enum types for non-PostgreSQL databases
old_cell_type_enum = sa.Enum("query", "text", "chart", name="datacelltype")
new_cell_type_enum = sa.Enum("query", "text", "chart", "python", name="datacelltype")

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    ErrorText = sa.Text(length=65535)
    conn = op.get_bind()
    dialect = conn.dialect.name
    if dialect == "postgresql":
        ErrorText = sa.Text()
        # PostgreSQL: Add new enum value to existing 'datacelltype' enum
        op.execute("ALTER TYPE datacelltype ADD VALUE 'python'")
    else:
        # Other Databases (e.g., MySQL, SQLite): Alter 'data_cell.cell_type' column to use the new enum
        op.alter_column(
            "data_cell",
            "cell_type",
            existing_type=old_cell_type_enum,
            type_=new_cell_type_enum,
        )
    op.create_table(
        "python_cell_result",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("data_cell_id", sa.Integer(), nullable=False),
        sa.Column("output", sa.JSON(), nullable=True),
        sa.Column("error", ErrorText, nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["data_cell_id"], ["data_cell.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("data_cell_id"),
        mysql_charset="utf8mb4",
        mysql_engine="InnoDB",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("python_cell_result")

    # ### Enum Modifications ###
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "postgresql":
        # PostgreSQL: does not support removing enum values directly
        # We need to create a new enum without 'python', rename the old one, and update the column
        op.execute("ALTER TYPE datacelltype RENAME TO datacelltype_old")
        old_cell_type_enum.create(bind, checkfirst=True)
        op.execute(
            "ALTER TABLE data_cell ALTER COLUMN cell_type TYPE datacelltype USING cell_type::text::datacelltype"
        )
        op.execute("DROP TYPE datacelltype_old")
    else:
        # Other Databases (e.g., MySQL, SQLite): Revert 'data_cell.cell_type' column to the old enum
        op.alter_column(
            "data_cell",
            "cell_type",
            existing_type=new_cell_type_enum,
            type_=old_cell_type_enum,
        )
    # ### end Alembic commands ###
