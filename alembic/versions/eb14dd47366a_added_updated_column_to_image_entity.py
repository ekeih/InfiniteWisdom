"""added 'updated' column to Image entity

Revision ID: eb14dd47366a
Revises: 8c7e750c5f11
Create Date: 2021-01-30 19:50:12.180532

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'eb14dd47366a'
down_revision = '8c7e750c5f11'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('images', sa.Column('updated', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('images', 'updated')
    # ### end Alembic commands ###
