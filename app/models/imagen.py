from datetime import datetime
from ..extensions import db

class Imagen(db.Model):
    __tablename__ = 'imagenes'
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    es_principal = db.Column(db.Boolean, default=False)
    orden = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Llave foránea
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    
    def __repr__(self):
        return f'<Imagen {self.id}>'