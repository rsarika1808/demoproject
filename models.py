from datetime import datetime
from hashlib import md5

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app import login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    created_on = db.Column(db.DateTime, index=True, default=datetime.now)
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def __repr__(self):
        return '<User {}>'.format(self.username)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class MyUpload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file = db.Column(db.String(255))
    path = db.Column(db.String(255))
    extension = db.Column(db.String(4))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_on = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return self.path


class JobDescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    details = db.Column(db.String)
    title = db.Column(db.Integer, nullable=True)
    category = db.Column(db.String(50))
    keywords = db.Column(db.String(255))
    created_on = db.Column(db.DateTime, index=True, default=datetime.now)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'{self.title} ({self.category})'


class Info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    category = db.Column(db.String(10))
    location = db.Column(db.String)
    created_on = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return self.name


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(32))
    message = db.Column(db.String(255))
    created_on = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return f'{self.name} message'
