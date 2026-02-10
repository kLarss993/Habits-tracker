from flask import *

import models

app = Flask(__name__)
app.secret_key = 'maybe_secret_key'
models.init_db()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register')
def register():
    return render_template('registre.html')

@app.route('/login')
def login():
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
