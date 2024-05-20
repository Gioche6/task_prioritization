from flask import render_template, flash, redirect, url_for, request, Blueprint
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from app.models import User, Task
from urllib.parse import urlparse
from app.forms import LoginForm, RegistrationForm, TaskForm

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', title='Home', tasks=tasks)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET, POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route('/add_task', methods=['GET', 'POST'])
@login_required
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(body=form.body.data, author=current_user, category=form.category.data, priority=form.priority.data, deadline=form.deadline.data)
        db.session.add(task)
        db.session.commit()
        flash('Your task is now live!')
        return redirect(url_for('main.index'))
    return render_template('add_task.html', title='Add Task', form=form)

@bp.route('/task_matrix')
@login_required
def task_matrix():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('task_matrix.html', title='Task Matrix', tasks=tasks)

@bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='Profile')

@bp.route('/complete_task/<task_id>')
@login_required
def complete_task(task_id):
    task = Task.query.get(task_id)
    if task and task.author == current_user:
        task.completed = True
        db.session.commit()
        flash('Task marked as complete!')
    return redirect(url_for('main.index'))

@bp.route('/delete_task/<task_id>')
@login_required
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task and task.author == current_user:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted!')
    return redirect(url_for('main.index'))

@bp.route('/update_task_category', methods=['POST'])
@login_required
def update_task_category():
    data = request.get_json()
    task = Task.query.get(data['taskId'])
    if task and task.author == current_user:
        task.category = data['category']
        db.session.commit()
        return '', 204
    return '', 403
