from core.factory import HitFactory
from web import app


def _init_factory():
    return HitFactory(app)


@app.get('/<string:hash_key>')
def redirect(hash_key):
    return _init_factory().handle_redirect(hash_key)

@app.get('/stats/<string:hash_key>')
def stats(hash_key):
    return _init_factory().handle_statistics(hash_key)