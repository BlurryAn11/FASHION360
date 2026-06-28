from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp

class LoginForm(FlaskForm):
    email = EmailField('Correo Electrónico', validators=[
        DataRequired(message='El correo es obligatorio'),
        Email(message='Correo inválido')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es obligatoria')
    ])
    submit = SubmitField('Iniciar Sesión')

class RegistroForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[
        DataRequired(message='El usuario es obligatorio'),
        Length(min=3, max=80, message='El usuario debe tener entre 3 y 80 caracteres'),
        Regexp('^[A-Za-z0-9_]+$', message='Solo letras, números y guión bajo')
    ])
    email = EmailField('Correo Electrónico', validators=[
        DataRequired(message='El correo es obligatorio'),
        Email(message='Correo inválido')
    ])
    nombre_completo = StringField('Nombre Completo', validators=[
        DataRequired(message='El nombre es obligatorio'),
        Length(min=3, max=150)
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es obligatoria'),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(message='Confirma tu contraseña'),
        EqualTo('password', message='Las contraseñas no coinciden')
    ])
    submit = SubmitField('Registrarse')