from infinitewisdom.persistence.pickle import PicklePersistence
from infinitewisdom.persistence.sqlalchemy import SQLAlchemyPersistence

p1 = PicklePersistence()
p2 = SQLAlchemyPersistence()

added = 0
skipped = 0
for e in p1._entities:
    if len(p2.find_by_url(e.url)) <= 0:
        print("Adding: {}".format(e.url))
        p2.add(e)
        added += 1
    else:
        print("Skipping: {}".format(e.url))
        skipped += 1

total = added + skipped

print("Added {}/{} entries ({} skipped)".format(added, total, skipped))
