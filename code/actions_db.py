from typing import Any

from models import Habits, Users


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

def delete_habit(user_id: int, name: str):
    Habits.delete().where((Habits.name == name) & (Habits.user == user_id)).execute()

def get_habit_category(name: str):
    habit = Habits.select().where(Habits.name == name)
    return habit.get().category

def get_habit_by_name(user_id: int, name: str):
    try:
        return Habits.get((Habits.name == name) & (Habits.user == user_id))
    except Habits.DoesNotExist:
        return None

def habit_update(name: str, category: str, user_id: int):
    Habits.update(category=category).where(Habits.name == name, Users.id == user_id).execute()

def add_user(name: str, password: str):
    Users.create(username=name, password=password)

def user_exists(name: str) -> bool:
    return Users.select().where(Users.username == name).exists()

def get_user_by_name(name: str):
    try:
        return Users.get(Users.username == name)
    except Users.DoesNotExist:
        return None

def get_user_id_by_name(name: str):
    user = Users.get(Users.username == name)
    return user.id

# def get_all_products_by_name_az(company_id: int):
#     return Product.select().where(Product.company == company_id).order_by(Product.name)
#
# def get_all_products_by_name_za(company_id: int):
#     return Product.select().where(Product.company == company_id).order_by(Product.name.desc())
#
# def get_all_products_cheapest_first(company_id: int):
#     return Product.select().where(Product.company == company_id).order_by(Product.price)
#
# def get_all_products_expensive_first(company_id: int):
#     return Product.select().where(Product.company == company_id).order_by(Product.price.desc())
#
# def get_products_by_category_(company_id: int, category: str) -> Any:
#     return Product.select().where((Product.category == category) & (Product.company == company_id))
#
# def is_password_valid(password: str) -> bool:
#         if len(password) >= 6:
#             have_letter = False
#             have_number = False
#             have_special = False
#             for i in password:
#                 if i.isalpha():
#                     have_letter = True
#                 if i.isdigit():
#                     have_number = True
#                 if not i.isalnum():
#                     have_special = True
#             if have_letter and have_number and have_special: