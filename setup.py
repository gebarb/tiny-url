import datetime
import json
from flask import Flask

from core.engine import HitEngine, UrlEngine


def _init_db(app):
    url_engine = UrlEngine(app=app)
    hit_engine = HitEngine(app=app)

    url_engine.create_tables()
    hit_engine.create_table()



def main():
    app = Flask(__name__)
    app.config.from_file('web/config.json', load=json.load)
    _init_db(app)


if __name__ == '__main__':
    main()
