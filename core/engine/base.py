class BaseEngine:

    def __init__(self, **kwargs):
        self.APP = kwargs.get('app', None)
        self.CONN_STRING = kwargs.get('conn_string', 'sqlite://test.db')

