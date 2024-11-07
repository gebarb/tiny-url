from sqlalchemy import select, and_, func
from core.engine.base import BaseEngine
from core.db import Database, Schema


class HitEngine(BaseEngine):
    def __init__(self, **kwargs):
        super(HitEngine, self).__init__(**kwargs)

        self.SCHEMA = Schema()

    def create_table(self):
        with Database(app=self.APP, conn_string=self.CONN_STRING) as db:
            h = self.SCHEMA.hit

            db.create(h)

    def create_hit(self, hit):
        with Database(app=self.APP, conn_string=self.CONN_STRING) as db:
            h = self.SCHEMA.hit

            q_ = h.insert().values(hit)

            db.execute(q_)

    def get_statistics(self, hash_key):
        with Database(app=self.APP, conn_string=self.CONN_STRING) as db:
            uh = self.SCHEMA.url_hash.alias('uh')
            u = self.SCHEMA.url.alias('u')
            h = self.SCHEMA.hit.alias('h')

            rc_ = [uh, u.c.url, func.count(h.c.id.distinct()).label('num_clicks')]
            wc_ = [uh.c.hash_key == hash_key]

            js_ = uh
            js_ = js_.join(u, uh.c.url_id == u.c.id)
            js_ = js_.outerjoin(h, uh.c.id == h.c.url_hash_id)

            q_ = select(*rc_).select_from(js_).where(and_(*wc_))

            return db.get(q_)
