from datetime import datetime
from sqlalchemy import select, and_
from core.engine.base import BaseEngine
from core.db import Database, Schema


class UrlEngine(BaseEngine):
    def __init__(self, **kwargs):
        super(UrlEngine, self).__init__(**kwargs)

        self.SCHEMA = Schema()

    def create_tables(self):
        with Database(app=self.APP, conn_string=self.CONN_STRING) as db:
            u = self.SCHEMA.url
            uh = self.SCHEMA.url_hash

            db.create(u)
            db.create(uh)

    def create_url(self, long_url):
        with Database(app=self.APP, conn_string=self.CONN_STRING) as db:
            u = self.SCHEMA.url

            # See if this url already exists
            wc_ = [u.c.url == long_url]

            q_ = u.select().where(and_(*wc_))
            url = db.get(q_)
            if url:
                return url.get('id')
            else:
                url = {
                    'url': long_url,
                    'date_created': datetime.now()
                }
                q_ = u.insert().values(url)
                return db.execute(q_)

    def create_url_hash(self, url_hash):
        with Database(app=self.APP, conn_string=self.CONN_STRING) as db:
            uh = self.SCHEMA.url_hash

            q_ = uh.insert().values(url_hash)

            return db.execute(q_)

    def get_url(self, hash_key):
        with Database(app=self.APP, conn_string=self.CONN_STRING) as db:
            uh = self.SCHEMA.url_hash.alias('uh')
            u = self.SCHEMA.url.alias('u')

            rc_ = [uh, u.c.url]
            wc_ = [uh.c.hash_key == hash_key]

            js_ = uh
            js_ = js_.join(u, uh.c.url_id == u.c.id)

            q_ = select(*rc_).select_from(js_).where(and_(*wc_))

            return db.get(q_)

    def delete_url(self, hash_key):
        with Database(app=self.APP, conn_string=self.CONN_STRING) as db:
            uh = self.SCHEMA.url_hash

            wc_ = [uh.c.hash_key == hash_key]

            q_ = uh.update().values(
                {'is_deleted': 1, 'date_modified': datetime.now()}).where(and_(*wc_))

            return db.execute(q_)
