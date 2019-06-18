from concurrent.futures.thread import ThreadPoolExecutor

from tqdm import tqdm

from infinitewisdom.config import Config
from infinitewisdom.persistence import ImageDataPersistence
from infinitewisdom.util import download_image_bytes, create_hash

config = Config()

p = ImageDataPersistence(config)

added = 0
skipped = 0
deleted = 0
errored = 0
current = 0

entities = p.get_all()
total = len(entities)
progress = tqdm(total=total, unit_scale=True, mininterval=1)


def migrate_entity(entity):
    global added
    global skipped
    global deleted
    global errored
    global current

    try:
        progress.set_postfix_str(entity.url)
        progress.update(n=1)

        if entity.image_hash is not None:
            existing_image_data = p._image_data_store.get(entity.image_hash)
            if existing_image_data is not None:
                existing_hash = create_hash(existing_image_data)
                if existing_hash == entity.image_hash:
                    skipped += 1
                    return

        try:
            image_data = download_image_bytes(entity.url)
        except:
            print(
                "d Deleted: '{}'".format(entity.url))
            p.delete(entity.url)
            deleted += 1
            return

        p.update(entity, image_data)
        print("+ Downloaded: '{}'".format(entity.url))
        added += 1
    except Exception as e:
        errored += 1
        print(e)
    finally:
        current = added + deleted + skipped + errored


with ThreadPoolExecutor(max_workers=16, thread_name_prefix="db-migration") as executor:
    for e in entities:
        future = executor.submit(migrate_entity, e)

print("Added {}\nDeleted {}\nSkipped {}\nTotal {} ".format(added, deleted, skipped, total))
