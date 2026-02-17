from peewee import *

db = SqliteDatabase('db.sqlite', pragmas={'foreign_keys': 1})


class BaseModel(Model):
    class Meta:
        database = db


class Users(BaseModel):
    username = TextField()
    password = TextField()


class Habits(BaseModel):
    name = TextField()
    category = TextField()
    days = IntegerField()
    weekdays = TextField()
    user = ForeignKeyField(Users, backref='products')


def init_db():
    db.connect()
    db.create_tables([Habits])
    db.create_tables([Users])