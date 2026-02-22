from flask import *

from habits.route import habits_bp
import models
from auth.route import auth_bp

app = Flask(__name__)

app.register_blueprint(auth_bp)
app.register_blueprint(habits_bp)
models.init_db()
app.secret_key = 'maybe_secret_key'

if __name__ == '__main__':
    app.run(debug=True)



