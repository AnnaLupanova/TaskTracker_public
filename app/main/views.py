from flask import render_template, url_for, request, redirect, flash, session, Blueprint
from flask_login import login_user, login_required, logout_user, current_user
from random import randint
from werkzeug.security import generate_password_hash, check_password_hash
from app.main.UserLogin import UserLogin
from app.main.forms import AddUser, AddProject, photos, editUser, AddTasks
from datetime import timedelta
from app.main.models import db, Users, Tasks, Projects, AllowedLinks, Statuses, Priorities,TaskUserLink
from app import login_manager
from sqlalchemy import or_, and_


SESSION_KEEPALIVE = timedelta(seconds=30)

main = Blueprint('main', __name__, template_folder='../templates')
print(__name__, '---')



@main.before_request
def before_request():
    session.permanent = True
    main.permanent_session_lifetime = timedelta(hours=1)
    # ALLOWED_LINKS_FOR_USERS = get_allowed_link()
    # print(ALLOWED_LINKS_FOR_USERS)


def get_allowed_link():
    allowed_link = AllowedLinks.query.filter_by(user_id=current_user.id).first()
    return allowed_link


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(Users).get(user_id)


# @main.teardown_appcontext
# def close_db(exception):
#     db = getattr(g, '_database', None)
#     if db is not None:
#         db.close()


@main.route('/')
@main.route('/home')
@login_required
def home():
    return redirect(url_for('main.get_tasks'))


@main.errorhandler(401)
def not_uthorized(error):
    return redirect(url_for("main.login"))


@main.errorhandler(404)
def not_found_page(error):
    return render_template('404_page.html')


@main.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = Users.query.filter_by(email=request.form['email']).first()
        if user and check_password_hash(user.password, request.form['password']):
            userlogin = UserLogin().create(user)
            login_user(userlogin)
            return redirect(url_for('main.home'))

        flash("Incorrect password or email", "error")

    return render_template('login.html')


@main.route('/projects', methods=['POST', 'GET'])
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


@main.route('/users', methods=['POST', 'GET'])
def get_users():
    users = Users.query.filter(and_(Users.id != current_user.id, Users.is_deleted==0)).all()
    args = {
        "content": users,
        "name_op_page": "users",
        "titles": ['First name', 'Last name', 'Email'],  # список названия столбцов
        "views_fields": ['first_name', 'last_name', 'email']  # список полей для отображения
    }
    show_modal = None
    return render_template("template_for_projects_and_users.html", args=args, show_modal=show_modal)


@main.route('/profile', methods=['POST', 'GET'])
def get_profile():
    form = editUser()
    return render_template('profile.html', form=form,user=current_user)


@main.route('/users/add', methods=['POST', 'GET'])
def add_user():
    users = Users.query.filter(and_(Users.id != current_user.id, Users.is_deleted==0)).all()
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
                if form.photo.data:
                    file = photos.save(form.photo.data, name=filename)

                    file_url = photos.url(file)
                db.session.add(Users(first_name=form.first_name.data,
                                     last_name=form.last_name.data,
                                     email=form.email.data,
                                     password=hash_psw,
                                     photo=file_url))
                db.session.commit()
                flash("User created", category="success")
                return redirect(url_for('main.get_users'))
            except Exception as e:
                flash(f"Have error while creating user <{str(e)}>", category="error")
                db.session.rollback()
                return redirect(url_for('main.get_users'))

    return render_template("template_for_projects_and_users.html", args=args, form=form, show_modal=show_modal)


@main.route('/projects/add', methods=['POST', 'GET'])
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
                return redirect(url_for('main.get_project'))
            except Exception as e:
                flash(f"Have error while creating project <{str(e)}>", category="error")
                db.session.rollback()
                return redirect(url_for('main.get_project'))

    return render_template("template_for_projects_and_users.html", args=args, form=form, show_modal=show_modal)


@main.route('/users/edit/<int:id>', methods=['POST', 'GET'])
def edit_user(id):
    user = Users.query.get(id)
    return render_template("_detail_user.html", user=user)


@main.route('/projects/edit/<int:id>', methods=['POST', 'GET'])
def edit_project(id):
    project = Projects.query.get(id)
    return render_template("_detail_project.html", project=project)


@main.route('/users/delete/<int:id>', methods=['POST', 'GET'])
def delete_user(id):
    user = Users.query.get_or_404(id)
    try:
        user.email = user.email + "_deleted"
        user.is_deleted = 1
        db.session.commit()
        flash("User has been deleted", category="success")
    except Exception as e:
        db.session.rollback()
        flash(f"Have error while deleting user <{e}>", category="error")
        db.session.rollback()
    return redirect(url_for("main.get_users"))


@main.route('/users/update/<int:id>', methods=['POST', 'GET'])
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
                return redirect(url_for('main.edit_user', id=id))
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


@main.route('/projects/update/<int:id>', methods=['POST', 'GET'])
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
                return redirect(url_for('.edit_project', id=id))
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


@main.route('/projects/delete/<int:id>', methods=['POST', 'GET'])
def delete_project(id):
    project = Projects.query.get_or_404(id)
    try:
        project.name = project.name + '_deleted'
        project.is_deleted = 1
        db.session.commit()
        flash("Project has been deleted", category="success")
    except Exception as e:
        db.session.rollback()
        flash(f"Have error while deleting project <{e}>", category="error")
        db.session.rollback()
    return redirect(url_for("main.get_project"))



@main.route('/tasks')
def get_tasks():
    query = db.session.query(
        Tasks.name,
        Tasks.description,
        Projects.name,
        Priorities.name,
        Statuses.name,
    )
    tasks = query.join(Projects).join(Statuses).join(Priorities)\
        .join(TaskUserLink).filter(TaskUserLink.user_to_id == current_user.id).order_by(Priorities.id).all()
    print(tasks)
    args = {
        "content": tasks,
        "name_op_page": "tasks",
        "titles": ['Name', 'Description', 'Project' , 'Priority', 'Status', ],  # список названия столбцов
    }

    show_modal = None
    return render_template("show_tasks.html", args=args, show_modal=show_modal)


@main.route('/tasks/add', methods=['POST', 'GET'])
def add_task():
    form = AddTasks()
    projects = Projects.query.filter_by(is_deleted=0).all()
    statuses = Statuses.query.all()
    priorities = Priorities.query.all()
    users = Users.query.filter(and_(Users.id != current_user.id,
                                    Users.is_deleted == 0))
    form.projects_id.choices = [(project.id, project.name) for project in projects]
    form.status_id.choices = [(status.id, status.name) for status in statuses]
    form.priority_id.choices = [(priority.id, priority.name) for priority in priorities]
    form.user_to_id.choices = [(user.id, f"{user.first_name} {user.last_name}") for user in users]

    if form.validate_on_submit():
        tasks = Tasks(name=form.name.data,
                             desc=form.description.data,
                             project_id=form.projects_id.data,
                             status_id=form.status_id.data,
                             priority_id=form.priority_id.data
        )
        db.session.add(tasks)
        db.session.commit()
        db.session.refresh(tasks)

        db.session.add(TaskUserLink(
                        task_id=tasks.id,
                        user_by_id=current_user.id,
                        user_to_id=form.user_to_id.data
        ))
        db.session.commit()

        return redirect(url_for('main.get_tasks'))

    return render_template('add_task.html',form=form)

@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

