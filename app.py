# IMPORTS
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_qrcode import QRcode
import logging
from flask_talisman import Talisman

# LOGGER
class SecurityFilter(logging.Filter):
    def filter(self, record):
        return 'SECURITY' in record.getMessage()  # Filter out any message that don't contain 'SECURITY'

logger = logging.getLogger()  # Get logger
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('lottery.log', 'a')  # Create File handler to handle and update the lottery.log file
file_handler.setLevel(logging.WARNING)

file_handler.addFilter(SecurityFilter())

formatter = logging.Formatter('%(asctime)s : %(message)s', '%m/%d/%Y %I:%M:%S %p')

file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

load_dotenv()

# CONFIG
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['RECAPTCHA_PUBLIC_KEY'] = os.getenv('RECAPTCHA_PUBLIC_KEY')
app.config['RECAPTCHA_PRIVATE_KEY'] = os.getenv('RECAPTCHA_PRIVATE_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_ECHO'] = os.getenv('SQLALCHEMY_ECHO') == 'True'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS') == 'True'

# initialise database
db = SQLAlchemy(app)

# Security headers
csp = {
    'default-src': ['\'self\''],
    'style-src': ['\'self\'', 'https://cdnjs.cloudflare.com/ajax/libs/bulma/0.7.2/css/bulma.min.css'],
    'script-src': ['\'self\'', '\'unsafe-inline\'', 'https://www.google.com/recaptcha/', 'https://www.gstatic.com/recaptcha/'],
    'frame-src': ['\'self\'', 'https://www.google.com/recaptcha/'],
    'img-src': ['data:'],
}

# initialise security headers
talisman = Talisman(app, content_security_policy=csp)

qrcode = QRcode(app)
migrate = Migrate(app, db)


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

# LOGIN MANAGER
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.init_app(app)


from models import User
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))  # Get user id from table



if __name__ == "__main__":
    app.run(ssl_context=('cert.pem', 'key.pem'), debug=False)



