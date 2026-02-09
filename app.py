from flask import *

app = Flask(__name__)
app.secret_key = 'artem-kotenko'


@app.route('/')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)