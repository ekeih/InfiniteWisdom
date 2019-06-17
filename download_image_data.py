from concurrent.futures.thread import ThreadPoolExecutor

from infinitewisdom.persistence.sqlalchemy import SQLAlchemyPersistence
from infinitewisdom.util import download_image_bytes, create_hash

p1 = SQLAlchemyPersistence(url="sqlite:///infinitewisdom.db")

added = 0
skipped = 0
deleted = 0
current = 0


def migrate_entity(entity):
    global added
    global skipped
    global deleted
    global current

    try:
        if entity.image_data is None:
            try:
                image_data = download_image_bytes(entity.url)
                image_hash = create_hash(image_data)
            except:
                print(
                    "d Deleted: '{}'".format(
                        entity.url))
                p1.delete(entity.url)
                deleted += 1
                return

            entity.image_data = image_data
            entity.image_hash = image_hash
            p1.update(entity)
            print("+ Downloaded: '{}'".format(entity.url))
            added += 1
        else:
            print("O Skipped '{}'".format(entity.url))
            skipped += 1
    finally:
        current = added + skipped
        print("Progress: {}/{}".format(current, total))


with ThreadPoolExecutor(max_workers=4, thread_name_prefix="db-migration") as executor:
    entities = p1.find_without_image_data()
    total = len(entities)
    for e in entities:
        future = executor.submit(migrate_entity, e)

print("Added {}/{} entries ({} skipped)".format(added, total, skipped))
