from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from forms import RegistrationForm, LoginForm 
from models import User, Journal 
from extensions import db
from datetime import datetime
import uuid
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

db.init_app(app)

migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@app.route('/')
def home():
    if current_user.is_authenticated:
        return render_template('main.html')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data.lower()
        email = form.email.data.lower()

        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return render_template('register.html', form=form)
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use a different email or log in.', 'danger')
            return render_template('register.html', form=form)

        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(form.password.data)
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Your account has been created successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Error during registration: {str(e)}')
            flash('An unexpected error occurred. Please try again later.', 'danger')

    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check your email and password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))



@app.route('/journals')
@login_required
def view_journals():
    #get journals for that user
    journals = Journal.query.filter_by(account_id=current_user.id).all()
    return render_template('main.html', journals=journals)

@app.route('/journals/new', methods=['GET', 'POST'])
@login_required
def new_journal():
    if request.method == 'POST':
        id = str(uuid.uuid4().hex)
        now = datetime.utcnow()
        content = str(request.form['content'])
        future = str(request.form['future'])

        new_journal = Journal(id=id, 
        date=now, 
        content=content, 
        future=future, 
        comment="", 
        account_id=current_user.id)

        # print(type(id), type(date), type(content), type(future), type(current_user.id))
        
        db.session.add(new_journal)
        db.session.commit()
        return redirect(url_for('view_journals'))
    return render_template('new_journal.html')

@app.route('/abc')
@login_required
def show_journal():
    journals = current_user.journals
    return render_template('journals.html', journals=journals)

with app.app_context():
    db.create_all()