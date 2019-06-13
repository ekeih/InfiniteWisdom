from infinitewisdom.persistence.pickle import PicklePersistence
from infinitewisdom.persistence.sqlalchemy import SQLAlchemyPersistence

p1 = PicklePersistence("D:\\temp")
p2 = SQLAlchemyPersistence()

for e in p1._entities:
    if len(p2.find_by_url(e.url)) <= 0:
        print("Adding: {}".format(e.url))
        p2.add(e)
    else:
        print("Skipping: {}".format(e.url))
