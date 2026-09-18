from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileField, FileAllowed

class PatientSignupForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female')])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class DoctorSignupForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    specialization = SelectField('Specialization', choices=[
        ('cardiology', 'Cardiology'),
        ('neurology', 'Neurology'),
        ('orthopedics', 'Orthopedics'),
        ('pediatrics', 'Pediatrics'),
        ('dermatology', 'Dermatology'),
        ('general', 'General Medicine'),
        # Add more specializations as needed
    ], validators=[DataRequired()])
    qualifications = StringField('Qualifications')
    phone = StringField('Phone', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female')])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class ProfileUpdateForm(FlaskForm):
    address = StringField('Address')
    state = StringField('State')
    blood_group = StringField('Blood Group')
    physically_challenged = StringField('Physically Challenged')
    photo = FileField('Photo', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update Profile')


class AppointmentForm(FlaskForm):
    doctor = SelectField('Doctor', coerce=int, validators=[DataRequired()])
    appointment_date = DateField('Appointment Date', format='%Y-%m-%d', validators=[DataRequired()])
    reason = TextAreaField('Reason')
    submit = SubmitField('Book Appointment')

class AppointmentUpdateForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('Scheduled','Scheduled'),
        ('Completed','Completed'),
        ('Rescheduled','Rescheduled')
    ])
    new_date = DateField('New Appointment Date', format='%Y-%m-%d')
    disease = TextAreaField('Disease / Notes')
    submit = SubmitField('Update Appointment')
