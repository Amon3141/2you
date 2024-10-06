from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

class Journal(db.Model):
    __tablename__ = 'journals'

    id = db.Column(db.String(100), primary_key=True)
    date = db.Column(db.Date())
    content = db.Column(db.String(5000))
    future = db.Column(db.String(5000))
    comment = db.Column(db.String(1000))
    account_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', back_populates='journals')

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    journals = db.relationship('Journal', back_populates='user', lazy=True)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)