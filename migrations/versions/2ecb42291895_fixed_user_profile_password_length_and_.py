"""fixed user_profile password length and rename

Revision ID: 2ecb42291895
Revises: 91c022f2ad4f
Create Date: 2023-06-09 11:48:11.910122

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '2ecb42291895'
down_revision = '91c022f2ad4f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user_profile', 'password', new_column_name='hash_password',
                    existing_type=sa.String(length=255),
                    nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user_profile', 'hash_password', new_column_name='password',
                    existing_type=sa.String(length=40),
                    nullable=False)
    # ### end Alembic commands ###