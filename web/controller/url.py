from core.factory import UrlFactory
from web import app


def _init_factory():
    return UrlFactory(app)


@app.get('/url/<string:hash_key>')
def get_long_url(hash_key):
    return _init_factory().handle_get_long_url(hash_key)


@app.post('/url')
@app.post('/url/create')
def create_short_url():
    return _init_factory().handle_create_short_url()



@app.delete('/url/<string:hash_key>')
def delete_short_url(hash_key):
    return _init_factory().handle_delete_short_url(hash_key)
