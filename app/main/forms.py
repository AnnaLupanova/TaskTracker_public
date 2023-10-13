from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Regexp
from app.main.models import Users, Projects
from flask_wtf.file import FileField, FileAllowed
from wtforms.widgets import PasswordInput
import re
from flask_uploads import UploadSet, IMAGES

photos = UploadSet('photos', IMAGES)


class AddUser(FlaskForm):
    email = StringField("Email: ", validators=[DataRequired(), Email(), Length(min=4, max=50)],
                        render_kw={'class': 'form-control '})
    first_name = StringField("First name: ", validators=[DataRequired(), Length(min=4, max=40,
                                                                                message='Name field must be at least %(min)d characters long '
                                                                                        'and %(max)d at most.')],
                             render_kw={'class': 'form-control '})
    last_name = StringField("Last name: ", validators=[DataRequired(), Length(min=4, max=40,
                                                                              message='Name field must be at least %(min)d characters long '
                                                                                      'and %(max)d at most.')],
                            render_kw={'class': 'form-control '})
    password = PasswordField("Password: ", validators=[DataRequired(),
                                                       Regexp(r"^(?=.*?[a-z])(?=.*?[0-9]).{6,}$",
                                                              message='Length of at least 6 characters, '
                                                                      'at least one letter and at least one number')],
                             render_kw={'class': 'form-control'})
    photo = FileField(validators=[FileAllowed(photos, 'Image only!')])

    submit = SubmitField("Save", render_kw={'class': 'btn btn-primary'})

    def validate_email(self, field):
        if Users.query.filter_by(email=field.data).first():
            raise ValidationError(u'User with the same email already created')


class editUser(FlaskForm):

    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        super().__init__(*args, **kwargs)

    email = StringField("Email: ", validators=[DataRequired(), Email(), Length(min=4, max=50)],
                        render_kw={'class': 'form-control '})
    first_name = StringField("First name: ", validators=[DataRequired(), Length(min=4, max=40,
                                                                                message='Name field must be at least %(min)d characters long '
                                                                                        'and %(max)d at most.')],
                             render_kw={'class': 'form-control '})
    last_name = StringField("Last name: ", validators=[DataRequired(), Length(min=4, max=40,
                                                                              message='Name field must be at least %(min)d characters long '
                                                                                      'and %(max)d at most.')],
                            render_kw={'class': 'form-control '})

    password = StringField("Password: ", validators=[], render_kw={'class': 'form-control'},
                           widget=PasswordInput(hide_value=False), default="old_password_input")
    photo = FileField(validators=[FileAllowed(photos, 'Image only!')])

    submit = SubmitField("Save", render_kw={'class': 'btn btn-primary'})

    def validate_email(self, field):
        user = Users.query.filter_by(email=field.data).first()
        if user:
            if self.kwargs["id"] != user.id:
                raise ValidationError(u'User with the same email already created')

    def validate_password(self, field):
        if field.data != "old_password_input":
            if not re.match(r"^(?=.*?[a-z])(?=.*?[0-9]).{6,}$", field.data):
                raise ValidationError(u'Length of at least 6 characters, at least one letter and at least one number')


class AddProject(FlaskForm):

    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        super().__init__(*args, **kwargs)

    name = StringField("Name: ", render_kw={'class': 'form-control '}, validators=[DataRequired(), Length(min=4, max=40,
                                                                                                          message='Name field must be at least %(min)d characters long '
                                                                                                                  'and %(max)d at most.')])
    description = TextAreaField("Description", render_kw={'class': 'form-control '},
                                validators=[DataRequired(), Length(min=10, max=300,
                                                                   message='Field must be at least %(min)d characters long '
                                                                           'and %(max)d at most.')])
    submit = SubmitField("Save", render_kw={'class': 'btn btn-primary'})

    def validate_name(self, field):
        project = Projects.query.filter_by(name=field.data.lower()).first()
        if project:
            if "id" in self.kwargs:
                if self.kwargs["id"] != project.id:
                    raise ValidationError(u'User with the same email already created')
            else:
                raise ValidationError(u'Projects with the same email already created')


class AddTasks(FlaskForm):
    name = StringField("Name", render_kw={'class': 'form-control '}, validators=[DataRequired(), Length(min=4, max=40,
                                                                                                          message='Name field must be at least %(min)d characters long '
                                                                                                                  'and %(max)d at most.')])
    description = TextAreaField("Description", render_kw={'class': 'form-control '},
                                validators=[DataRequired(), Length(max=500)])
    projects_id = SelectField("Select project", coerce=int, render_kw={'class': 'form-control '})
    status_id = SelectField("Select status", coerce=int, render_kw={'class': 'form-control '})
    priority_id = SelectField("Select priority", coerce=int, render_kw={'class': 'form-control '})
    user_to_id = SelectField("Executor", coerce=int, render_kw={'class': 'form-control '})

    submit = SubmitField("Add",  render_kw={'class': 'btn btn-primary'})
