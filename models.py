from flask_sqlalchemy import SQLAlchemy

from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

association_table = db.Table('association',
                             db.Column('user_by_id', db.Integer, db.ForeignKey('users.id')),
                             db.Column('user_to_id', db.Integer, db.ForeignKey('users.id')),
                             db.Column('task_id', db.ForeignKey('tasks.id')))


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

    def __repr__(self):
        return '<Task id {}>'.format(self.id)


class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, db.Sequence("users_id_seq", start=1), primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    users_task = db.relationship("Users", secondary=association_table,
                                 primaryjoin=(association_table.c.user_by_id == id),
                                 secondaryjoin=(association_table.c.user_to_id == id),
                                 backref=db.backref('association', lazy='dynamic'),
                                 lazy='dynamic')

    allowlinks = db.relationship("AllowedLinks", backref="users")

    photo = db.Column(db.String(500), default=None)

    def __init__(self, first_name, last_name, email, password, photo):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.photo = photo
        self.role_id = 2

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
