from flask import *

app = Flask(__name__)
app.secret_key = 'artem-kotenko'


@app.route('/')
def home():
    flash('hi')
    flash('hello')
    flash('skebob')

    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
