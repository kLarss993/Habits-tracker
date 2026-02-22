from flask import *

from habits.route import habits_bp

from auth.route import auth_bp

app = Flask(__name__)

app.register_blueprint(auth_bp)
app.register_blueprint(habits_bp)


if __name__ == '__main__':
    app.run(debug=True)



