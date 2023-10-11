from flask import Flask, render_template, url_for, request, g, redirect, flash, make_response, session
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from random import randint
from werkzeug.security import generate_password_hash, check_password_hash
from UserLogin import UserLogin
from forms import AddUser, AddTasks, AddProject, photos, editUser
from datetime import timedelta

SESSION_KEEPALIVE = timedelta(seconds=30)

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
app.config['SECRET_KEY'] = 'bf054a49ce6d9ba109a091824a0441c9edfc58e4'

app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'uploads')

configure_uploads(app, photos)
patch_request_class(app)

login_manager = LoginManager(app)


from models import db, Users, Tasks, Priorities, Projects, Statuses, AllowedLinks

db.init_app(app)
migrate = Migrate(app, db)



@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(hours=1)


def get_allowed_link():
    allowed_link = AllowedLinks.query.filter_by(user_id=current_user.id).first()
    return allowed_link


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(Users).get(user_id)


@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()




@app.route('/')
@app.route('/home')
@login_required
def home():
    content = render_template('index.html')
    res = make_response(content)
    return res


@app.errorhandler(401)
def not_uthorized(error):
    return redirect(url_for("login"))


@app.errorhandler(404)
def not_found_page(error):
    return render_template('404_page.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = Users.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password, request.form['password']):
            userlogin = UserLogin().create(user)
            login_user(userlogin)
            return redirect(url_for('home'))

        flash("Incorrect password or email", "error")

    return render_template('login.html')


@app.route('/projects', methods=['POST', 'GET'])
@login_required
def get_project():
    projects = Projects.query.filter(Projects.is_deleted == 0).all()
    args = {
        "content": projects,
        "name_op_page": "projects",
        "titles": ['Name', 'Description'],  # список названия столбцов
        "views_fields": ['name', 'description']  # список полей для отображения
    }

    show_modal = None
    return render_template("template_for_projects_and_users.html", args=args, show_modal=show_modal)


@app.route('/users', methods=['POST', 'GET'])
def get_users():
    users = Users.query.all()
    args = {
        "content": users,
        "name_op_page": "users",
        "titles": ['First name', 'Last name', 'Email'],  # список названия столбцов
        "views_fields": ['first_name', 'last_name', 'email']  # список полей для отображения
    }
    show_modal = None
    return render_template("template_for_projects_and_users.html", args=args, show_modal=show_modal)


@app.route('/users/add', methods=['POST', 'GET'])
def add_user():
    users = Users.query.all()
    args = {
        "content": users,
        "name_op_page": "users",
        "titles": ['First name', 'Last name', 'Email'],  # список названия столбцов
        "views_fields": ['first_name', 'last_name', 'email']  # список полей для отображения
    }
    form = AddUser()
    show_modal = True
    file_url = None
    if form.is_submitted():
        if form.validate_on_submit():
            try:
                hash_psw = generate_password_hash(form.password.data, salt_length=8)
                filename = f"img_{form.first_name.data}_{randint(0, 0xFFFFFFFF)}."
                file = photos.save(form.photo.data, name=filename)

                file_url = photos.url(file)
                db.session.add(Users(first_name=form.first_name.data,
                                     last_name=form.last_name.data,
                                     email=form.email.data,
                                     password=hash_psw,
                                     photo=file_url))
                db.session.commit()
                flash("User created", category="success")
                return redirect(url_for('get_users'))
            except Exception as e:
                flash(f"Have error while creating user <{str(e)}>", category="error")
                db.session.rollback()
                return redirect(url_for('get_users'))

    return render_template("template_for_projects_and_users.html", args=args, form=form, show_modal=show_modal)


@app.route('/projects/add', methods=['POST', 'GET'])
def add_project():
    projects = Projects.query.filter(Projects.is_deleted == 0).all()
    args = {
        "content": projects,
        "name_op_page": "projects",
        "titles": ['Name', 'Description'],  # список названия столбцов
        "views_fields": ['name', 'description']  # список полей для отображения
    }
    form = AddProject()
    show_modal = True
    if form.is_submitted():
        if form.validate_on_submit():
            try:
                db.session.add(Projects(form.name.data.lower(), form.description.data))
                db.session.commit()
                flash("Project created", category="success")
                return redirect(url_for('get_project'))
            except Exception as e:
                flash(f"Have error while creating project <{str(e)}>", category="error")
                db.session.rollback()
                return redirect(url_for('get_project'))

    return render_template("template_for_projects_and_users.html", args=args, form=form, show_modal=show_modal)


@app.route('/users/edit/<int:id>', methods=['POST', 'GET'])
def edit_user(id):
    user = Users.query.get(id)
    return render_template("_detail_user.html", user=user)


@app.route('/projects/edit/<int:id>', methods=['POST', 'GET'])
def edit_project(id):
    project = Projects.query.get(id)
    return render_template("_detail_project.html", project=project)


@app.route('/users/delete/<int:id>', methods=['POST', 'GET'])
def delete_user(id):
    user = Users.query.get_or_404(id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash("User has been deleted", category="success")
    except Exception as e:
        db.session.rollback()
        flash(f"Have error while deleting user <{e}>", category="error")
        db.session.rollback()
    return redirect(url_for("get_users"))


@app.route('/users/update/<int:id>', methods=['POST', 'GET'])
@login_required
def update_user(id):
    form = editUser(id=id)
    user = Users.query.get(id)
    show_modal = True
    if form.is_submitted():
        if form.validate_on_submit():
            try:
                if user:
                    user.first_name = form.first_name.data
                    user.last_name = form.last_name.data
                    user.email = form.email.data
                    hash_psw = generate_password_hash(form.password.data, salt_length=8)
                    user.password = hash_psw
                    print(form.password.data)
                    if form.photo.data:
                        filename = f"img_{form.first_name.data}_{randint(0, 0xFFFFFFFF)}."
                        file = photos.save(form.photo.data, name=filename)
                        file_url = photos.url(file)
                        user.photo = file_url
                    db.session.commit()
                    flash("User updated", category="success")
                return redirect(url_for('edit_user', id=id))
            except Exception as e:
                flash(f"Have error while updating user <{e}>", category="error")
                db.session.rollback()
    else:
        if user:
            form.first_name.default = user.first_name
            form.last_name.default = user.last_name
            form.email.default = user.email
            form.process()
    #
    return render_template("_detail_user.html", form=form, user=user, show_modal=show_modal)


@app.route('/projects/update/<int:id>', methods=['POST', 'GET'])
@login_required
def update_project(id):
    form = AddProject(id=id)
    project = Projects.query.get(id)
    show_modal = True
    if form.is_submitted():
        if form.validate_on_submit():
            try:
                if project:
                    project.name = form.name.data
                    project.description = form.description.data

                    db.session.commit()
                    flash("Project updated", category="success")
                return redirect(url_for('edit_project', id=id))
            except Exception as e:
                flash(f"Have error while updating project <{e}>", category="error")
                db.session.rollback()
    else:
        if project:
            form.name.default = project.name
            form.description.default = project.description
            form.process()
    #
    return render_template("_detail_project.html", form=form, project=project, show_modal=show_modal)


@app.route('/projects/delete/<int:id>', methods=['POST', 'GET'])
def delete_project(id):
    project = Projects.query.get_or_404(id)
    try:
        db.session.delete(project)
        db.session.commit()
        flash("Project has been deleted", category="success")
    except Exception as e:
        db.session.rollback()
        flash(f"Have error while deleting project <{e}>", category="error")
        db.session.rollback()
    return redirect(url_for("get_project"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.app_context().push()
    # db.create_all()
    app.run(debug=True)
    # app.run()
