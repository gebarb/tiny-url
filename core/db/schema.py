from sqlalchemy import Column, ForeignKey, MetaData, Table
from sqlalchemy.dialects.sqlite import INTEGER, TEXT, DATETIME


class Schema:
    url = Table(
        'url', MetaData(),
        Column('id', INTEGER, primary_key=True, nullable=False),
        Column('url', TEXT,  nullable=False),
        Column('date_created', DATETIME, nullable=False)
    )

    url_hash = Table(
        'url_hash', MetaData(),
        Column('id', INTEGER, primary_key=True, nullable=False),
        Column('hash_key', TEXT,  nullable=False),
        Column('url_id', INTEGER, ForeignKey(url.c.id), nullable=False),
        Column('date_created', DATETIME, nullable=False),
        Column('date_modified', DATETIME, nullable=True),
        Column('is_deleted', INTEGER, nullable=False, default=0)
    )

    hit = Table(
        'hit', MetaData(),
        Column('id', INTEGER, primary_key=True, nullable=False),
        Column('url_hash_id', INTEGER, ForeignKey(url_hash.c.id)),
        Column('ip_address', TEXT,  nullable=True),
        Column('user_agent', TEXT,  nullable=True),
        Column('date_created', DATETIME, nullable=False)
    )
