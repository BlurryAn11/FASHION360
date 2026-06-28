from app import create_app
from app.extensions import db
from app.models import Imagen

app = create_app()

with app.app_context():
    img = Imagen.query.first()
    if img:
        img.es_principal = True
        db.session.commit()
        print(f"✅ Imagen {img.id} marcada como principal")
        
        if img.url and img.url.startswith('/static/'):
            img.url = img.url.replace('/static/', '/uploads/')
            db.session.commit()
            print(f"✅ URL corregida: {img.url}")
        else:
            print(f"ℹ️ URL: {img.url}")
    else:
        print("⚠️ No hay imágenes en la base de datos")
