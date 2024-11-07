from web import app


@app.get('/')
def index():
    return 'Hello, Tiny URL!'
