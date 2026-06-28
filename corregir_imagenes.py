from app import create_app
from app.extensions import db
from app.models import Imagen

app = create_app()

with app.app_context():
    imagenes = Imagen.query.all()
    
    if not imagenes:
        print("⚠️ No hay imágenes en la base de datos")
        print("   Sube una imagen desde el panel admin primero.")
        exit()
    
    print(f"📋 Encontradas {len(imagenes)} imágenes")
    
    for img in imagenes:
        # CORREGIR URL
        if img.url:
            # Si la URL tiene /static/, lo quitamos
            if '/static/' in img.url:
                img.url = img.url.replace('/static/', '/uploads/')
            
            # Si la URL no empieza con /uploads/, lo agregamos
            if not img.url.startswith('/uploads/'):
                nombre = img.url.split('/')[-1]
                img.url = f'/uploads/productos/{nombre}'
            
            # Si no hay ninguna principal, marcar la primera como principal
            if not Imagen.query.filter_by(producto_id=img.producto_id, es_principal=True).first():
                img.es_principal = True
            
            db.session.commit()
            print(f"✅ Imagen {img.id}: URL -> {img.url}, Principal: {img.es_principal}")
    
    print("\n✅ Todas las imágenes corregidas")
