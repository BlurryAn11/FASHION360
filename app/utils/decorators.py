from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def role_required(*roles):
    """Decorador para verificar roles de usuario"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Por favor inicia sesión', 'warning')
                return redirect(url_for('auth.login'))
            
            if current_user.rol not in roles:
                flash('No tienes permisos para acceder a esta página', 'danger')
                return redirect(url_for('shop.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator