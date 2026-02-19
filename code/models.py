from peewee import *

db = SqliteDatabase('db.sqlite', pragmas={'foreign_keys'})


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


class HabitCompletion(BaseModel):
    habit = ForeignKeyField(Habits, backref='completions')
    date = DateField()

    class Meta:
        indexes = (
            (('habit', 'date'), True),
        )


def init_db():
    db.connect()
    db.create_tables([Users, Habits, HabitCompletion])