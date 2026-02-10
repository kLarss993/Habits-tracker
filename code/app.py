from flask import *
from werkzeug.security import generate_password_hash

import models
import re
from actions_db import *

app = Flask(__name__)
app.secret_key = 'maybe_secret_key'
models.init_db()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username:
            flash("Login required")
            return redirect("/register")

        if len(password) < 8:
            flash("Password must be at least 8 characters")
            return redirect("/register")

        if not re.search(r"[A-Za-zА-Яа-яІіЇїЄєҐґ]", password):
            flash("Password must contain only letters, numbers and dashes")
            return redirect("/register")

        if user_exists(username):
            flash(f'User "{username}" already exists')
            return redirect(url_for('register'))

        heshed_password = generate_password_hash(password)

        add_user(username, heshed_password)
        flash(f'User "{username}" was successfully registered')
        return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
