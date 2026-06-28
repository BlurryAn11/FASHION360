from flask import Flask
from .config import DevelopmentConfig, ProductionConfig, TestingConfig
from .extensions import db, migrate, login_manager, bcrypt, csrf


def create_app(config_name='development'):
    """Application Factory Pattern"""
    
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Cargar configuración
    if config_name == 'development':
        app.config.from_object(DevelopmentConfig)
    elif config_name == 'production':
        app.config.from_object(ProductionConfig)
    elif config_name == 'testing':
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(DevelopmentConfig)
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    
    # Registrar blueprints
    from .blueprints.auth import auth_bp
    from .blueprints.admin import admin_bp
    from .blueprints.shop import shop_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(shop_bp, url_prefix='/')
    
    # ===== RUTA PARA SERVIR IMÁGENES =====
    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        from flask import send_from_directory
        import os
        uploads = os.path.join(app.root_path, 'static', 'uploads')
        return send_from_directory(uploads, filename)
    
    # Crear tablas si no existen
    with app.app_context():
        db.create_all()
    
    return app