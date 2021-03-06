"""Initial state

Revision ID: 6ef730f2340b
Revises: 
Create Date: 2019-06-18 16:54:06.752267

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '6ef730f2340b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('images',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('url', sa.String(), nullable=True),
                    sa.Column('text', sa.String(), nullable=True),
                    sa.Column('analyser', sa.String(), nullable=True),
                    sa.Column('analyser_quality', sa.Float(), nullable=True),
                    sa.Column('created', sa.Float(), nullable=True),
                    sa.Column('telegram_file_id', sa.String(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('images')
    # ### end Alembic commands ###
