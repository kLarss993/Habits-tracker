from datetime import datetime, timedelta

from flask import *

from models import *
from actions_db import *

app = Flask(__name__)
habits_bp = Blueprint('habits', __name__, template_folder='templates')
now = datetime.now()
init_db()
app.secret_key = 'maybe_secret_key'

week_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
weekday_to_num = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}

today = datetime.now()
dates = []
for i in range(6, -1, -1):
    date = today - timedelta(days=i)
    dates.append(date.strftime('%m/%d'))

def is_logged():
    return 'username' in session

def current_user():
    if 'username' not in session:
        return None
    return get_user_by_name(session['username']) # Потрібно повернути об'єкт користувача

def get_habit_calendar_dates(weekdays_str, num_days, start_date=None):
    if not weekdays_str or not weekdays_str.strip():
        return {}

    weekday_list = [wd.strip() for wd in weekdays_str.split(',')]
    weekday_list = [wd for wd in weekday_list if wd in weekday_to_num]

    if not weekday_list:
        return {}

    calendar_data = {}
    today = start_date or datetime.now().date()

    occurrences_per_weekday = num_days // len(weekday_list)
    remainder = num_days % len(weekday_list)

    for idx, weekday_name in enumerate(weekday_list):
        target_weekday = weekday_to_num[weekday_name]
        dates = []

        occurrences = occurrences_per_weekday + (1 if idx < remainder else 0)

        days_ahead = target_weekday - today.weekday()
        if days_ahead < 0:
            days_ahead += 7

        next_date = today + timedelta(days=days_ahead)

        for i in range(occurrences):
            date = next_date + timedelta(weeks=i)
            dates.append(date)

        calendar_data[weekday_name] = dates

    return calendar_data

@habits_bp.route('/', methods=['GET', 'POST'])
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

    return render_template('habits/templates/habits/home.html', username=username, now=now, dates=dates, habits=sorted_habits,
                           completed=completed)

@habits_bp.route('/add_habit', methods=['GET', 'POST'])
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
    return render_template('habits/templates/habits/add_habit.html', week_days=week_days)

@habits_bp.route('/about_habit/<habit_name>')
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
        'habits/templates/habits/about_habit.html',
        habit=habit,
        calendar_dates=calendar_dates,
        completion_dates=[d.isoformat() for d in completion_dates],
        today=today_date,
        days_remaining=days_remaining,
        completed_today=completed_today,
        can_complete_today=can_complete_today,
        habit_name=habit_name,
    )


@habits_bp.route('/complete_today/<habit_name>', methods=['POST'])
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

@habits_bp.route('/delete/<name>')
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
