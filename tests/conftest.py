# -*- coding: utf-8 -*-

from uuid import uuid4
from os import environ

from pytest import fixture

from rio.app import create_app
from rio.core import db as db

@fixture(scope='session')
def app(request):
    environ['RIO_ENV'] = 'test'
    app_ = create_app()
    ctx = app_.app_context()
    ctx.push()
    request.addfinalizer(ctx.pop)
    return app_


@fixture(scope='session')
def database(request, app):
    uuid = uuid4().hex
    for table in db.metadata.sorted_tables:
        table.name = 'test_%s_%s' % (uuid, table.name)
    db.create_all()
    def fin():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
    request.addfinalizer(fin)
    return db

@fixture
def session(request, database):
    # cache.mc._flushall()
    def fin():
        for table in reversed(database.metadata.sorted_tables):
            database.session.execute(table.delete())
        database.session.commit()
        database.session.close()
        # cache.mc._flushall()
    request.addfinalizer(fin)
    return database.session

@fixture
def client(app, request):
    ctx = app.test_request_context()
    ctx.push()
    request.addfinalizer(ctx.pop)
    return app.test_client()
