"""generate_pdf_request create poincare_path

Revision ID: 4d6c61b0f027
Revises: 9dde9394bc03
Create Date: 2023-06-01 15:38:17.769525

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4d6c61b0f027'
down_revision = '9dde9394bc03'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('generate_pdf_request', sa.Column('poincare_path', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('generate_pdf_request', 'poincare_path')
    # ### end Alembic commands ###