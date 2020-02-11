from concurrent.futures.thread import ThreadPoolExecutor

from tqdm import tqdm

from infinitewisdom.config.config import AppConfig
from infinitewisdom.persistence import ImageDataPersistence
from infinitewisdom.util import download_image_bytes, create_hash

config = AppConfig(validate=False)
config.SQL_PERSISTENCE_URL.value = "postgresql://infinitewisdom:infinitewisdom@localhost/infinitewisdom"
config.FILE_PERSISTENCE_BASE_PATH.value = "/mnt/sdb1/infinitewisdom"
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
            existing_image_data = p.get_image_data(entity)
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
            p.delete(entity)
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


with ThreadPoolExecutor(max_workers=8, thread_name_prefix="db-migration") as executor:
    for e in entities:
        future = executor.submit(migrate_entity, e)

# for e in entities:
#    migrate_entity(e)

print("Added {}\nDeleted {}\nSkipped {}\nTotal {} ".format(added, deleted, skipped, total))
