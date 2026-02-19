from typing import Any

from models import Habits, Users, HabitCompletion


def get_all_habits(user_id: int):
    return Habits.select().where(Habits.user == user_id)

def get_habits_by_category(user_id: int, category: str) -> Any:
    return Habits.select().where((Habits.category == category) & (Habits.user == user_id))

def habit_exists(user_id: int, name: str) -> bool:
    return Habits.select().where((Habits.name == name) & (Habits.user == user_id)).exists()

def get_all_categories(user_id: int):
    return Habits.select(Habits.category).where(Habits.user == user_id).distinct().order_by(Habits.category)

def add_habits(user_id: int, name: str, category: str, days: int, weekdays: str):
    Habits.create(user=user_id, name=name, category=category, days=days, weekdays=weekdays)

# def delete_habit(user_id: int, name: str):
#     habit = Habits.get_or_none((Habits.name == name) & (Habits.user == user_id))
#     if not habit:
#         return  HabitCompletion.delete().where(HabitCompletion.habit == habit).execute() & Habits.delete().where(Habits.id == habit.id).execute()

def delete_habit(user_id: int, name: str):
    # Шукаємо звичку
    habit = Habits.get_or_none((Habits.name == name) & (Habits.user == user_id))

    if habit:
        # 1. Спочатку видаляємо всі відмітки про виконання цієї звички
        HabitCompletion.delete().where(HabitCompletion.habit == habit.id).execute()

        # 2. Потім видаляємо саму звичку
        Habits.delete().where(Habits.id == habit.id).execute()

def get_habit_category(name: str):
    habit = Habits.select().where(Habits.name == name)
    return habit.get().category

def get_habit_by_name(user_id: int, name: str):
        return Habits.get((Habits.name == name) & (Habits.user == user_id))


def habit_update(name: str, category: str, user_id: int):
    Habits.update(category=category).where(Habits.name == name, Users.id == user_id).execute()


def mark_habit_completed(habit_id: int, date):
    HabitCompletion.get_or_create(habit=habit_id, date=date)


def get_habit_completions(habit_id: int):
    return HabitCompletion.select().where(HabitCompletion.habit == habit_id)

def add_user(name: str, password: str):
    Users.create(username=name, password=password)

def user_exists(name: str) -> bool:
    return Users.select().where(Users.username == name).exists()

def get_user_by_name(name: str):
    # Поверне None, якщо користувача немає, замість того щоб "ламати" програму
    return Users.get_or_none(Users.username == name)

def get_user_id_by_name(name: str):
    user = Users.get_or_none(Users.username == name)
    return user.id if user else None