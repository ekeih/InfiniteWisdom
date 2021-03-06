"""migrate telegram_file_id to its own table to allow multiple values

Revision ID: 76e388cb011b
Revises: a7b7c2c9b5c2
Create Date: 2019-08-14 01:01:02.509759

"""
import logging

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '76e388cb011b'
down_revision = 'a7b7c2c9b5c2'
branch_labels = None
depends_on = None


def upgrade():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # ### commands auto generated by Alembic - please adjust! ###
    new_telegram_file_ids_table = op.create_table('telegram_file_ids',
                                                  sa.Column('id', sa.String(), nullable=False),
                                                  sa.Column('image_id', sa.Integer(), nullable=True),
                                                  sa.ForeignKeyConstraint(['image_id'], ['images.id'], ),
                                                  sa.PrimaryKeyConstraint('id')
                                                  )

    conn = op.get_bind()
    res = conn.execute("select id, telegram_file_id from images")

    logger.info("Fetching existing data...")

    results = res.fetchall()

    logger.info("Creating new entity data...")
    telegram_file_ids = [{'image_id': r[0], 'id': r[1]} for r in results]

    logger.info("Filtering None entries...")
    telegram_file_ids = list(filter(lambda x: x['id'] is not None, telegram_file_ids))

    def chunks(l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    i = 0
    chunk_length = 100
    total_count = len(telegram_file_ids)
    for chunk in chunks(telegram_file_ids, chunk_length):
        logger.info("Processing chunk {}, processed items {}/{}...".format(i, i * chunk_length, total_count))
        op.bulk_insert(new_telegram_file_ids_table, chunk)
        i += 1

    op.drop_index('ix_images_telegram_file_id', table_name='images')
    op.drop_column('images', 'telegram_file_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('images', sa.Column('telegram_file_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.create_index('ix_images_telegram_file_id', 'images', ['telegram_file_id'], unique=False)
    op.drop_table('telegram_file_ids')
    # ### end Alembic commands ###
