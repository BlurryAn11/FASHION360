from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, DecimalField, IntegerField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class CategoriaForm(FlaskForm):
    nombre = StringField('Nombre de la Categoría', validators=[
        DataRequired(message='El nombre es obligatorio'),
        Length(min=2, max=100, message='Mínimo 2 caracteres')
    ])
    descripcion = TextAreaField('Descripción', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Guardar Categoría')

class MarcaForm(FlaskForm):
    nombre = StringField('Nombre de la Marca', validators=[
        DataRequired(message='El nombre es obligatorio'),
        Length(min=2, max=100)
    ])
    descripcion = TextAreaField('Descripción', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Guardar Marca')

class ProductoForm(FlaskForm):
    nombre = StringField('Nombre del Producto', validators=[
        DataRequired(message='El nombre es obligatorio'),
        Length(min=2, max=150)
    ])
    descripcion = TextAreaField('Descripción')
    precio = DecimalField('Precio (Bs)', validators=[
        DataRequired(message='El precio es obligatorio'),
        NumberRange(min=0, message='El precio debe ser mayor a 0')
    ])
    stock = IntegerField('Stock', validators=[
        DataRequired(message='El stock es obligatorio'),
        NumberRange(min=0, message='El stock no puede ser negativo')
    ])
    categoria_id = SelectField('Categoría', coerce=int, validators=[DataRequired()])
    marca_id = SelectField('Marca', coerce=int, validators=[DataRequired()])
    destacado = BooleanField('Destacar producto')
    submit = SubmitField('Guardar Producto')

class ImagenForm(FlaskForm):
    """Formulario para subir imágenes"""
    imagen = FileField('Imagen del producto', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Solo imágenes permitidas (jpg, jpeg, png, gif, webp)'),
        FileRequired(message='Selecciona una imagen')
    ])
    es_principal = BooleanField('Marcar como imagen principal')
    submit = SubmitField('Subir Imagen')
