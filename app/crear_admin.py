from app import create_app
from app.extensions import db
from app.models import User

app = create_app()

with app.app_context():
    # Verificar si ya existe un admin
    admin_exists = User.query.filter_by(rol='admin').first()
    
    if admin_exists:
        print(f"⚠️ Ya existe un administrador: {admin_exists.email}")
        print("No se creará otro.")
    else:
        admin = User(
            username='admin',
            email='admin@fashion360.com',
            nombre_completo='Administrador del Sistema',
            rol='admin',
            activo=True
        )
        admin.set_password('admin123')
        
        db.session.add(admin)
        db.session.commit()
        
        print("Administrador creado exitosamente")
        print("Email: admin@fashion360.com")
        print("Contraseña: admin123")
        print("Cambia la contraseña después del primer inicio de sesión")