from sqlite3 import IntegrityError
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from forms import RegistrationForm, LoginForm 
from models import User, Journal, Affirmation
from extensions import db
from datetime import datetime, timedelta
import uuid, random
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

db.init_app(app)

migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@app.route('/new-entry')
@login_required
def home():
    if current_user.is_authenticated:
        journals = current_user.journals
        return render_template('entry.html', journals=journals)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
    
@app.route('/')
@login_required
def dashboard():
    affirmations = current_user.affirmations
    affirmation1 = random.choice(affirmations)
    affirmation2 = random.choice(affirmations)
    affirmation3 = random.choice(affirmations)
    journals = current_user.journals
    affirmations = current_user.affirmations
    affirmation1 = random.choice(affirmations)
    affirmation2 = random.choice(affirmations)
    affirmation3 = random.choice(affirmations)
    return render_template("dashboard.html", journals=journals,affirmation1=affirmation1, affirmation2=affirmation2, affirmation3=affirmation3)

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
            password=generate_password_hash(form.password.data)
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Your account has been created successfully! You can now log in.', 'success')
            return redirect(url_for('show_profile_creater'))
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
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
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

@app.route('/journals/new', methods=['GET', 'POST'])
@login_required
def new_journal():
    if request.method == 'POST':
        id = str(uuid.uuid4().hex)
        today = datetime.today().date()
        content = str(request.form['content'])
        future = str(request.form['future'])
        startDateDelta = int(request.form['startDate'])
        endDateDelta = startDateDelta + 7
        startDate = today + timedelta(days=startDateDelta)
        endDate = today + timedelta(days=endDateDelta)

        new_journal = Journal(
            id=id, 
            date=today,
            content=content, 
            future=future, 
            comment="", 
            account_id=current_user.id,
            startDate=startDate,
            endDate=endDate,
        )

        # print(type(id), type(date), type(content), type(future), type(current_user.id))
        
        db.session.add(new_journal)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('new_journal.html')

@app.route('/abc')
@login_required
def show_journal():
    journals = current_user.journals
    return render_template('journals.html', journals=journals)

# @app.route('/profile')
# @login_required
# def edit_profile(methods=['POST']):
#     if request.method == 'POST':
#         text = str(request.form['content'])
#         new_affirmation = Affirmation(text=text,accountid=accountid)
#         db.session.add(new_affirmation)
#         db.session.commit()
#         # return redirect(url_for('dashboard'))
#         return jsonify({"message": "success"})

#     return render_template('affirmation.html')

@app.route('/add_affirmation', methods=['POST'])
@login_required
def add_affirmation():
    text = request.form.get('content')

    if text:
        new_affirmation = Affirmation(
            text=text, 
            accountid=current_user.id)

        db.session.add(new_affirmation)
        db.session.commit()
        flash('Affirmation added successfully!', 'success')
    else:
        flash('Affirmation content cannot be empty.', 'danger')

    return redirect(url_for('home'))

@app.route('/profile/creator')
@login_required
def show_profile_creater():
    return render_template('affirmation.html')

@app.route('/profile')
@login_required
def show_affirmations():
    affirmations = current_user.affirmations
    affirmation1 = random.choice(affirmations)
    affirmation2 = random.choice(affirmations)
    affirmation3 = random.choice(affirmations)
    return render_template('dashboard.html', affirmation1=affirmation1, affirmation2=affirmation2, affirmation3=affirmation3)
    return render_template('dashboard.html', affirmation1=affirmation1, affirmation2=affirmation2, affirmation3=affirmation3)

@app.route('/journal/<string:journal_id>')
@login_required
def view_journal(journal_id):
    journal = Journal.query.get_or_404(journal_id)
    return render_template('view_journal.html', journal=journal)

with app.app_context():
    db.create_all()