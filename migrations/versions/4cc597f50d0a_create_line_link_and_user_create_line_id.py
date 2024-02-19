"""create line link and user create line_id

Revision ID: 4cc597f50d0a
Revises: 0129e4d72198
Create Date: 2023-04-21 12:50:03.033667

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4cc597f50d0a'
down_revision = '0129e4d72198'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('line_link',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('line_id', sa.String(length=255), nullable=False),
    sa.Column('uuid', sa.Integer(), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=False),
    sa.Column('linked_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['uuid'], ['user.uuid'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('user', sa.Column('line_id', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'line_id')
    op.drop_table('line_link')
    # ### end Alembic commands ###
