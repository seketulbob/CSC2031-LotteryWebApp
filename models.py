import pyotp
import pyotp.totp

from app import db, app
from flask_login import UserMixin
from datetime import datetime
from cryptography.fernet import Fernet, InvalidToken
import bcrypt


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # User authentication information.
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

    # User information
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False, default='user')
    pin_key = db.Column(db.String(32), nullable=False, default=pyotp.random_base32())
    registered_on = db.Column(db.DateTime, nullable=True)  # Change nullable=False
    current_login = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    post_key = db.Column(db.BLOB, nullable=True)  # Change nullable=False

    # Define the relationship to Draw
    draws = db.relationship('Draw')

    def __init__(self, email, firstname, lastname, phone, password, role):
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.phone = phone
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.role = role
        self.registered_on = datetime.now()
        self.current_login = None
        self.last_login = None
        self.post_key = Fernet.generate_key()

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password)

    def get_2fa_uri(self):
        return str(pyotp.totp.TOTP(self.pin_key).provisioning_uri(name=self.email, issuer_name='Lottery'))

    def verify_pin(self, pin):
        return pyotp.TOTP(self.pin_key).verify(pin)


def encrypt(data, post_key):
    return Fernet(post_key).encrypt(bytes(data, 'utf-8'))

def decrypt(data, post_key):
    return Fernet(post_key).decrypt(data).decode('utf-8')


class Draw(db.Model):
    __tablename__ = 'draws'

    id = db.Column(db.Integer, primary_key=True)

    # ID of user who submitted draw
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)

    # 6 draw numbers submitted
    numbers = db.Column(db.String(100), nullable=False)

    # 6 decrypted draw numbers (for matching against winning draw)
    decrypted_numbers = db.Column(db.String(100))

    # Draw has already been played (can only play draw once)
    been_played = db.Column(db.BOOLEAN, nullable=False, default=False)

    # Draw matches with master draw created by admin (True = draw is a winner)
    matches_master = db.Column(db.BOOLEAN, nullable=False, default=False)

    # True = draw is master draw created by admin. User draws are matched to master draw
    master_draw = db.Column(db.BOOLEAN, nullable=False)

    # Lottery round that draw is used
    lottery_round = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, user_id, numbers, master_draw, lottery_round, post_key):
        self.user_id = user_id
        self.numbers = encrypt(numbers, post_key)
        self.decrypted_numbers = None
        self.been_played = False
        self.matches_master = False
        self.master_draw = master_draw
        self.lottery_round = lottery_round

    def view_draw(self, post_key):
        self.decrypted_numbers = decrypt(self.numbers, post_key)
        self.numbers = decrypt(self.numbers, post_key)

    def decrypt_numbers(self, post_key):
        return decrypt(self.numbers, post_key) if self.numbers else None


def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        admin = User(email='admin@email.com',
                     password='Admin1!',
                     firstname='Alice',
                     lastname='Jones',
                     phone='0191-123-4567',
                     role='admin')

        db.session.add(admin)
        db.session.commit()
