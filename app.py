from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

db = SQLAlchemy(app)

login_manager = loginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'please login'

# creates the journal object
# journal has a date, content, future, and comment
class Journal(db.Model):
    date = db.Column(db.Date(), default=date.utcnow)
    content = db.Column(db.Text())
    future = db.Column(db.Text())
    comment = db.Column(db.Text(), nullable=True)

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.string(100), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




@app.route('/')
def home():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)