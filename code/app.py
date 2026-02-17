import re
from datetime import datetime, timedelta

from flask import *
from werkzeug.security import generate_password_hash, check_password_hash

import models
from actions_db import *

app = Flask(__name__)
app.secret_key = 'maybe_secret_key'
models.init_db()
now = datetime.now()

week_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

today = datetime.now()
dates = []
for i in range(6, -1, -1):  # 6 days ago to today (7 days total)
    date = today - timedelta(days=i)
    dates.append(date.strftime('%m/%d'))

def is_logged():
    return 'username' in session

def current_user():
    if 'username' not in session:
        return None

    user = get_user_by_name(session['username'])
    if not user:
        session.pop('username')
        return None

    return user


@app.route('/', methods=['GET', 'POST'])
def home():
    global dates
    if is_logged():
        username = session.get('username', 'Guest')
    else:
        flash('Please log in')
        return redirect(url_for('login'))

    user = current_user()
    completed = session.get('task_completed', False)

    if not user:
        session.pop('username', None)
        flash('Please log in again')
        return redirect(url_for('login'))

    # if request.method == 'POST':
    #     name = request.form.get('name')
    #     category = request.form.get('category')
    #     user_id = request.form.get('company_id')
    #
    #     if habit_exists(user.id, name):
    #         flash('Такий товар вже є!')
    #     else:
    #         add_habits(user_id, name, category)
    #         flash('Товар додано!')
    #         return redirect(url_for('home'))



    sorted_habits = get_all_habits(user.id)
    if request.form.get('search'):
        search = request.form.get('search')
        for habit in sorted_habits:
            if search not in habit['name']:
                sorted_habits.remove(habit)

    return render_template('home.html', username=username, now=now, dates=dates, habits=sorted_habits, completed=completed)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('username')
        password = request.form.get('password')

        if not name:
            flash("Login required")
            return redirect("/register")

        if len(password) < 8:
            flash("Password must be at least 8 characters")
            return redirect("/register")

        if not re.search(r"[A-Za-zА-Яа-яІіЇїЄєҐґ]", password):
            flash("Password must contain at least 1 letter")
            return redirect("/register")

        if user_exists(name):
            flash(f'User "{name}" already exists')
            return redirect(url_for('register'))

        password = generate_password_hash(password)

        add_user(name, password)
        flash(f'User "{name}" was successfully registered')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = get_user_by_name(username)

        if not user:
            flash(f'User "{username}" not exists!')
            return redirect(url_for('login'))

        if not check_password_hash(user.password, password):
            flash('Password incorrect!')
            return redirect(url_for('login'))

        session['username'] = user.username
        flash('You are logged in')
        return redirect(url_for('home'))

    return render_template('login.html')

@app.route('/add_habit', methods=['GET', 'POST'])
def add_habit():
    if is_logged():
        username = session.get('username')
        user_id = get_user_id_by_name(username)
    else:
        flash('Please log in')
        return redirect(url_for('login'))
    if request.method == 'POST':
        habit_name = request.form.get('new_habit_name')
        habit_category = request.form.get('new_habit_category')
        days = int(request.form.get('days'))
        weekdays_list = request.form.getlist('weekdays')
        habit_weekdays = ', '.join(weekdays_list)
        if habit_exists(user_id, habit_name):
            flash('Habit already exists')
            return redirect(url_for('home'))
        else:
            add_habits(user_id, habit_name, habit_category, days, habit_weekdays)
            flash('Habit added')
            return redirect(url_for('home'))
    week_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    return render_template('add_habit.html', week_days=week_days)


@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username')
        return redirect(url_for('login'))
    else:
        flash('You are log out')
        return redirect(url_for('login'))

# @app.route('/completion/<habit_name>'):
# if is_logged():
#     username = session.get('username')
#


@app.route('/delete/<name>')
def delete(name):
    if not is_logged():
        return redirect(url_for('login'))

    user = current_user()

    if habit_exists(user.id, name):
        delete_habit(user.id, name)
        flash(f'Habit {name} was successfully deleted')
    else:
        flash('Habit does not exist')

    return redirect('/')



if __name__ == '__main__':
    app.run(debug=True)



