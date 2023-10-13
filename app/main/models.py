from flask_sqlalchemy import SQLAlchemy

from flask_login import UserMixin
from datetime import datetime
from datetime import datetime

today = datetime.today
db = SQLAlchemy()

# association_table = db.Table('association',
#                              db.Column('user_by_id', db.Integer, db.ForeignKey('users.id')),
#                              db.Column('user_to_id', db.Integer, db.ForeignKey('users.id')),
#                              db.Column('task_id', db.ForeignKey('tasks.id')))

class TaskUserLink(db.Model):
    __tablename__ = 'task_user_link'
    user_by_id = db.Column(db.Integer, db.ForeignKey('users.id'),primary_key=True)
    user_to_id = db.Column(db.Integer, db.ForeignKey('users.id'),primary_key=True)
    task_id = db.Column(db.ForeignKey('tasks.id'), primary_key=True)

    def __init__(self,user_by_id, user_to_id, task_id):
        self.user_by_id = user_by_id
        self.user_to_id = user_to_id
        self.task_id = task_id

    def __repr__(self):
        return f"Task_id={self.task_id}, user_by_id={self.user_by_id}"


class Tasks(db.Model, UserMixin):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, db.Sequence("tasks_id_seq", start=1), primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(300))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('statuses.id'))
    priority_id = db.Column(db.Integer, db.ForeignKey('priorities.id'))
    is_active = db.Column(db.Integer, default=1)

    def __init__(self, name, desc,project_id, status_id, priority_id):
        self.name = name
        self.description = desc
        self.project_id = project_id
        self.status_id = status_id
        self.priority_id = priority_id
        self.created_date = today()
        self.updated_date = today()
        self.is_active = 1

    def __repr__(self):
        return f'<Task id={self.id}, name={self.name}, prior={self.priority_id},' \
               f'project_id={self.project_id}, status={self.status_id}>'


class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, db.Sequence("users_id_seq", start=1), primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    users_task = db.relationship("Users", secondary='task_user_link',
                                 primaryjoin=('TaskUserLink.user_by_id==Users.id'),
                                 secondaryjoin=('TaskUserLink.user_to_id==Users.id'),
                                 backref=db.backref('task_user_link', lazy='dynamic'),
                                 lazy='dynamic')
    allowlinks = db.relationship("AllowedLinks", backref="users")
    photo = db.Column(db.String(500), default=None)
    is_deleted = db.Column(db.Integer, default=0)
    #tasks = db.relationship('Tasks', secondary='task_user_link')

    def __init__(self, first_name, last_name, email, password, photo):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.photo = photo
        self.role_id = 2
        self.is_deleted = 0

    def __repr__(self):
        return f'User id={self.id}, name={self.first_name}, email={self.email}'


class AllowedLinks(db.Model, UserMixin):
    __tablename__ = 'allowed_links'
    id = db.Column(db.Integer, db.Sequence("allowed_links_id_seq", start=1), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    can_show_users = db.Column(db.Integer, default=0)
    can_create_projects = db.Column(db.Integer, default=0)

    def __init__(self, can_show_users, can_create_projects):
        self.can_show_users = can_show_users
        self.can_create_projects = can_create_projects

    def __repr__(self):
        return f'Allowed user_id={self.user_id},can_show_users={self.can_show_users}, ' \
               f'can_create_projects={self.can_create_projects} '


class Roles(db.Model, UserMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, db.Sequence("roles_id_seq", start=1), primary_key=True)
    name = db.Column(db.String(100), unique=True)
    is_super_user = db.Column(db.Integer, default=0)
    users = db.relationship("Users", backref="roles")

    def __repr__(self):
        return '<Role id {}>'.format(self.id)


class Projects(db.Model, UserMixin):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, db.Sequence("projects_id_seq", start=1), primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(300))
    is_deleted = db.Column(db.Integer, default=0)
    task = db.relationship("Tasks", backref="projects")

    def __init__(self, name, desc):
        self.name = name
        self.description = desc
        self.is_deleted = 0

    def __repr__(self):
        return '<Project id={}, name={}>'.format(self.id, self.name)


#
class Priorities(db.Model, UserMixin):
    __tablename__ = 'priorities'
    id = db.Column(db.Integer, db.Sequence("priority_id_seq", start=1), primary_key=True)
    name = db.Column(db.String(100), unique=True)
    status = db.relationship("Tasks", backref="priorities")

    def __repr__(self):
        return '<Priority id={}, name={}>'.format(self.id, self.name)


#
class Statuses(db.Model, UserMixin):
    __tablename__ = 'statuses'
    id = db.Column(db.Integer, db.Sequence("status_id_seq", start=1), primary_key=True)
    name = db.Column(db.String(100), unique=True)
    is_end_task = db.Column(db.Integer)
    task = db.relationship("Tasks", backref="statuses")

    def __repr__(self):
        return '<Status id={}, name={}>'.format(self.id, self.name)
#
#
