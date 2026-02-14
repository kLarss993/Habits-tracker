import re
from datetime import datetime

from flask import *
from werkzeug.security import generate_password_hash, check_password_hash

import models
from actions_db import *

app = Flask(__name__)
app.secret_key = 'maybe_secret_key'
models.init_db()
now = datetime.now()

@app.route('/')
def home():
    if 'username' in session:
        username = session.get('username', 'Guest')
    else:
        flash('Please log in')
        return redirect(url_for('login'))

    return render_template(
        'home.html',
        now=now,
        username=username)

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

        if not user_exists(username):
            flash(f'User "{username}" not exists!')
            return redirect(url_for('login'))

        user = get_user_by_name(username)  # Отримуємо об'єкт
        if not check_password_hash(user.password, password):
            flash('Password incorrect!')
            return redirect(url_for('login'))

        session['username'] = user.username
        flash('You are logged in')
        return redirect(url_for('home'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username')
        return redirect(url_for('login'))
    else:
        flash('You are log out')
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)


    #зробить видалення звичок
    #зробить редагування звичок
    #зробить табличку для перегляду звичок
    #зробить шоб можна було задавать за скільки днів виконать звичку

            #показувати поточний рік та місяць за допомогою бібліотеки time

    #в табличці має буть 14 кружків, коли користувач пройшов перші 7, мають появитись нові 7


