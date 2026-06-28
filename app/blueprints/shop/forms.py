from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class CheckoutForm(FlaskForm):
    direccion = StringField('Dirección de envío', validators=[
        DataRequired(message='La dirección es obligatoria'),
        Length(min=5, max=200, message='La dirección debe tener entre 5 y 200 caracteres')
    ])
    telefono = StringField('Teléfono de contacto', validators=[
        DataRequired(message='El teléfono es obligatorio'),
        Length(min=7, max=20, message='Teléfono inválido')
    ])
    notas = TextAreaField('Notas adicionales (opcional)')
    submit = SubmitField('Confirmar Pedido')