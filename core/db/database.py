
from typing import overload
from sqlalchemy import CursorResult, Sequence, Row, create_engine


class Database():

    def __init__(self, app=None, conn_string=None, isolation_level=None, is_transaction=False):
        self.APP = app
        self.ISOLATION_LEVEL = isolation_level
        self.IS_TRANSACTION = is_transaction

        self.ALIVE = False
        self.ERROR = False
        if self.APP:
            self.CONNECTION_STRING = self.APP.config.get('SQLALCHEMY_DATABASE_URI')
        else:
            self.CONNECTION_STRING = conn_string

        self.ALL = 1
        self.ONE = 2
        self.SCALAR = 3
        self.EXECUTE = 4

    def __enter__(self):
        if self.ISOLATION_LEVEL:
            self.CONNECTION = create_engine(
                self.CONNECTION_STRING, self.ISOLATION_LEVEL)
        else:
            self.CONNECTION = create_engine(self.CONNECTION_STRING)
        self.CURSOR = self.CONNECTION.connect()

        if self.IS_TRANSACTION:
            self.TRANSACTION = self.CURSOR.begin()

        self.ALIVE = True

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._terminate(exc_type is not None)

    def __del__(self):
        self._terminate()

    def _execute(self, query, action):
        match action:
            case self.ALL:
                results = self.CURSOR.execute(query).fetchall()
            case self.ONE:
                results = self.CURSOR.execute(query).first()
            case self.SCALAR:
                results = self.CURSOR.execute(query).scalar()
            case self.EXECUTE:
                results = self.CURSOR.execute(query)
            case _:
                results = None

        if not self.IS_TRANSACTION:
            self.CURSOR.commit()
        if results and isinstance(results, CursorResult):
            if results.is_insert:
                if results.inserted_primary_key and len(results.inserted_primary_key) > 0:
                    results = results.inserted_primary_key[0] or results.lastrowid

        return results

    @overload
    def _parse(self, data: Sequence[Row], **kwargs) -> dict:
        ...

    @overload
    def _parse(self, data: Row, **kwargs) -> list[dict]:
        ...

    def _parse(self, data: Sequence[Row] | Row, **kwargs) -> dict | list[dict] | None:
        if data is None:
            return None

        if isinstance(data, Row):
            return data._asdict()
        else:
            return [r._asdict() for r in data]

    def _terminate(self, error=False):
        if not self.ALIVE:
            return

        if self.IS_TRANSACTION:
            if self.ERROR or error:
                self.TRANSACTION.rollback()
            else:
                self.TRANSACTION.commit()
            self.IS_TRANSACTION = False

        self.CURSOR.close()
        self.CONNECTION.dispose()
        self.ALIVE = False

    def create(self, table):
        return table.create(self.CONNECTION, checkfirst=True)

    def execute(self, query):
        return self._execute(query, self.EXECUTE)

    def fetch(self, query):
        return self._parse(
            self._execute(query, self.ALL)
        )

    def get(self, query):
        return self._parse(
            self._execute(query, self.ONE)
        )

    def scalar(self, query):
        return self._parse(
            self._execute(query, self.SCALAR)
        )
