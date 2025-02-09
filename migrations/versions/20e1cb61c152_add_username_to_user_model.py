"""Add username to User model

Revision ID: 20e1cb61c152
Revises: bae03ea8c37b
Create Date: 2025-02-09 21:10:35.147176
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = '20e1cb61c152'
down_revision: Union[str, None] = 'bae03ea8c37b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # ### Step 1: Add columns as nullable ###
    op.add_column('users', sa.Column('username', sa.String(), nullable=True))
    op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=True))
    
    # ### Step 2: Backfill existing rows with unique default values ###
    conn = op.get_bind()
    result = conn.execute("SELECT id FROM users")
    for row in result:
        conn.execute(
            text("UPDATE users SET username = :username WHERE id = :id"),
            {"username": f"default_username_{row.id}", "id": row.id}
        )
        conn.execute(
            text("UPDATE users SET hashed_password = :password WHERE id = :id"),
            {"password": f"default_password_{row.id}", "id": row.id}
        )
    
    # ### Step 3: Alter columns to NOT NULL ###
    op.alter_column('users', 'username', nullable=False)
    op.alter_column('users', 'hashed_password', nullable=False)
    op.alter_column('users', 'email', existing_type=sa.VARCHAR(), nullable=False)
    
    # ### Step 4: Create index for the username column ###
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # ### Step 5: Drop the old 'name' column ###
    op.drop_column('users', 'name')

def downgrade() -> None:
    # ### Downgrade: Restore the 'name' column and drop new columns/index ###
    op.add_column('users', sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.alter_column('users', 'email', existing_type=sa.VARCHAR(), nullable=True)
    op.drop_column('users', 'hashed_password')
    op.drop_column('users', 'username')
