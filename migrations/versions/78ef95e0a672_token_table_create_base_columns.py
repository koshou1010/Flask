"""token table create base columns

Revision ID: 78ef95e0a672
Revises: ea02dab624ff
Create Date: 2023-05-03 14:10:20.489169

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '78ef95e0a672'
down_revision = 'ea02dab624ff'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('token', sa.Column('valid_flag', sa.Boolean(), nullable=False))
    op.add_column('token', sa.Column('create_user', sa.String(length=40), nullable=False))
    op.add_column('token', sa.Column('create_datetime', sa.DateTime(), nullable=False))
    op.add_column('token', sa.Column('update_user', sa.String(length=40), nullable=False))
    op.add_column('token', sa.Column('update_datetime', sa.DateTime(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('token', 'update_datetime')
    op.drop_column('token', 'update_user')
    op.drop_column('token', 'create_datetime')
    op.drop_column('token', 'create_user')
    op.drop_column('token', 'valid_flag')
    # ### end Alembic commands ###
