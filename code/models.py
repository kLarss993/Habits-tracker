from peewee import *

db = SqliteDatabase('db.sqlite', pragmas={'foreign_keys': 1})


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    name = TextField()
    password = TextField()


class Habits(BaseModel):
    name = TextField()
    type = TextField()
    category = TextField()
    user = ForeignKeyField(User, backref='products')


def init_db():
    db.connect()
    db.create_tables([Habits, User])