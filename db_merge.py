"""
Simple helper script to merge two databases (from p1 to p1).
If p1 has an entity not yet known to p2 it will be added.
Otherwise telegram_file_id values and better analyser values from p1 are used in p2.
"""

from concurrent.futures.thread import ThreadPoolExecutor

from tqdm import tqdm

from infinitewisdom.persistence.sqlalchemy import SQLAlchemyPersistence

p1 = SQLAlchemyPersistence(url="sqlite:///source_infinitewisdom.db")
p2 = SQLAlchemyPersistence(url="postgresql://infinitewisdom:infinitewisdom@localhost/infinitewisdom")

p1_total = p1.count()
added = 0
merged = 0

entities = p1.get_all()
total = len(entities)
progress = tqdm(total=total, unit_scale=True, mininterval=1)


def migrate_entity(entity):
    global added
    global merged
    global total

    progress.set_postfix_str(entity.image_hash)
    progress.update(n=1)

    p2_entity = p2.find_by_image_hash(entity.image_hash)
    if p2_entity is None:
        p2.add(entity)
        added += 1
    else:
        update = False
        if entity.analyser_quality is not None and (
                entity.analyser_quality is None or entity.analyser_quality < entity.analyser_quality):
            p2_entity.analyser = entity.analyser
            p2_entity.analyser_quality = entity.analyser_quality
            p2_entity.text = entity.text
            update = True

        if entity.telegram_file_id is not None and p2_entity.telegram_file_id is None:
            p2_entity.telegram_file_id = entity.telegram_file_id
            update = True

        if update:
            p2.update(p2_entity)
        merged += 1

    total = added + merged


with ThreadPoolExecutor(max_workers=4, thread_name_prefix="db-migration") as executor:
    for e in entities:
        future = executor.submit(migrate_entity, e)

print("Added {}/{} entries ({} merged)".format(added, total, merged))
