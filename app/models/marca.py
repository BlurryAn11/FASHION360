from datetime import datetime
from ..extensions import db

class Marca(db.Model):
    __tablename__ = 'marcas'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.String(255))
    logo = db.Column(db.String(255))  # Ruta del logo
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con productos
    productos = db.relationship('Producto', backref='marca', lazy=True)
    
    def __repr__(self):
        return f'<Marca {self.nombre}>'