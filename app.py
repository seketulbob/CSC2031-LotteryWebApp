# IMPORTS
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

# CONFIG
app = Flask(__name__)
app.config['SECRET_KEY'] = 'LongAndRandomSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lottery.db'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# initialise database
db = SQLAlchemy(app)


# HOME PAGE VIEW
@app.route('/')
def index():
    return render_template('main/index.html')

# ERRORS
@app.errorhandler(400)
def bad_request_error(error):
    return render_template('error/400.html')

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('error/403.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error/404.html')

@app.errorhandler(500)
def internal_error(error):
    return render_template('error/500.html')

@app.errorhandler(503)
def service_unavailable_error(error):
    return render_template('error/503.html')

# BLUEPRINTS
# import blueprints
from users.views import users_blueprint
from admin.views import admin_blueprint
from lottery.views import lottery_blueprint
#
# # register blueprints with app
app.register_blueprint(users_blueprint)
app.register_blueprint(admin_blueprint)
app.register_blueprint(lottery_blueprint)


if __name__ == "__main__":
    app.run()
