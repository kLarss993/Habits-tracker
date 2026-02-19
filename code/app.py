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
weekday_to_num = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}

today = datetime.now()
dates = []
for i in range(6, -1, -1):
    date = today - timedelta(days=i)
    dates.append(date.strftime('%m/%d'))


def get_habit_calendar_dates(weekdays_str, num_days, start_date=None):
    """
    Calculate dates for habit calendar.
    Based on the example: days=4, weekdays="Mon, Thu" shows 2 dates per weekday.
    Divides num_days evenly across the weekdays, with remainder distributed to first weekdays.
    Returns a dictionary: {weekday: [list of dates]}
    """
    if not weekdays_str or not weekdays_str.strip():
        return {}

    # Parse weekdays string: "Mon, Thu" -> ["Mon", "Thu"]
    weekday_list = [wd.strip() for wd in weekdays_str.split(',')]
    weekday_list = [wd for wd in weekday_list if wd in weekday_to_num]

    if not weekday_list:
        return {}

    calendar_data = {}
    # Anchor the calendar to a fixed start date so past
    # completed days stay visible instead of the window
    # moving forward every day.
    today = start_date or datetime.now().date()

    # Calculate occurrences per weekday (divide num_days evenly)
    occurrences_per_weekday = num_days // len(weekday_list)
    remainder = num_days % len(weekday_list)

    for idx, weekday_name in enumerate(weekday_list):
        target_weekday = weekday_to_num[weekday_name]
        dates = []

        # Add one extra occurrence for first 'remainder' weekdays
        occurrences = occurrences_per_weekday + (1 if idx < remainder else 0)

        # Find the next occurrence of this weekday (including today)
        days_ahead = target_weekday - today.weekday()
        if days_ahead < 0:
            days_ahead += 7

        # Get the first occurrence
        next_date = today + timedelta(days=days_ahead)

        # Get N occurrences (one per week)
        for i in range(occurrences):
            date = next_date + timedelta(weeks=i)
            dates.append(date)

        calendar_data[weekday_name] = dates

    return calendar_data


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

    sorted_habits = get_all_habits(user.id)
    if request.form.get('search'):
        search = request.form.get('search')
        for habit in sorted_habits:
            if search not in habit['name']:
                sorted_habits.remove(habit)

    return render_template('home.html', username=username, now=now, dates=dates, habits=sorted_habits,
                           completed=completed)


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


@app.route('/about_habit/<habit_name>')
def about_habit(habit_name):
    if not is_logged():
        flash('Please log in')
        return redirect(url_for('login'))

    user = current_user()
    if not user:
        flash('Please log in again')
        return redirect(url_for('login'))

    habit = get_habit_by_name(user.id, habit_name)
    if not habit:
        flash('Habit not found')
        return redirect(url_for('home'))

    # Ensure weekdays is a string (not a query object)
    weekdays_str = str(habit.weekdays) if habit.weekdays else ''

    # Completions and remaining days
    completions = list(get_habit_completions(habit.id))
    completion_dates = [c.date for c in completions]
    days_completed = len(completion_dates)
    days_remaining = max(habit.days - days_completed, 0)

    today_date = datetime.now().date()
    today_weekday_abbr = week_days[today_date.weekday()]
    weekday_list = [wd.strip() for wd in weekdays_str.split(',')] if weekdays_str else []
    is_today_scheduled = today_weekday_abbr in weekday_list
    completed_today = today_date in completion_dates
    can_complete_today = is_today_scheduled and not completed_today and days_remaining > 0

    # Anchor calendar to the earliest completion date if it exists,
    # otherwise to today. This keeps yesterday's completed slot visible.
    start_date = min(completion_dates) if completion_dates else today_date
    calendar_dates = get_habit_calendar_dates(weekdays_str, habit.days, start_date=start_date)

    return render_template(
        'about_habit.html',
        habit=habit,
        calendar_dates=calendar_dates,
        completion_dates=[d.isoformat() for d in completion_dates],
        today=today_date,
        days_remaining=days_remaining,
        completed_today=completed_today,
        can_complete_today=can_complete_today,
        habit_name=habit_name,
    )


@app.route('/complete_today/<habit_name>', methods=['POST'])
def complete_today(habit_name):
    if not is_logged():
        flash('Please log in')
        return redirect(url_for('login'))

    user = current_user()
    if not user:
        flash('Please log in again')
        return redirect(url_for('login'))

    habit = get_habit_by_name(user.id, habit_name)
    if not habit:
        flash('Habit not found')
        return redirect(url_for('home'))

    today_date = datetime.now().date()
    mark_habit_completed(habit.id, today_date)
    flash("You've completed this habit today")

    return redirect(url_for('about_habit', habit_name=habit.name))


@app.route('/delete/<name>')
def delete(name):
    if not is_logged():
        flash('Please log in')
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



