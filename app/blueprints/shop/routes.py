from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user

from . import shop_bp
from .forms import CheckoutForm
from app.models import Producto, Pedido, DetallePedido
from app.extensions import db
from app.extensions import csrf 
import random
import string


# ==================== TIENDA ====================

@shop_bp.route('/')
def index():
    productos = Producto.query.filter_by(activo=True, destacado=True).limit(8).all()
    return render_template('shop/index.html', productos=productos)


@shop_bp.route('/producto/<int:id>')
def producto_detalle(id):
    producto = Producto.query.get_or_404(id)
    return render_template('shop/producto.html', producto=producto)


# ==================== CARRITO ====================

def obtener_carrito():
    """Obtener el carrito de la sesión"""
    return session.get('carrito', {})


def guardar_carrito(carrito):
    """Guardar el carrito en la sesión"""
    session['carrito'] = carrito
    session.modified = True


def calcular_total(carrito):
    """Calcular el total del carrito"""
    total = 0
    for item in carrito.values():
        total += item['precio'] * item['cantidad']
    return total


@shop_bp.route('/carrito')
def ver_carrito():
    """Ver el contenido del carrito"""
    carrito = obtener_carrito()
    total = calcular_total(carrito)
    return render_template('shop/carrito.html', carrito=carrito, total=total)


@shop_bp.route('/carrito/agregar/<int:producto_id>', methods=['POST'])
@csrf.exempt
def agregar_al_carrito(producto_id):
    """Agregar un producto al carrito"""
    producto = Producto.query.get_or_404(producto_id)
    
    if producto.stock <= 0:
        flash('Producto agotado', 'danger')
        return redirect(url_for('shop.producto_detalle', id=producto_id))
    
    cantidad = int(request.form.get('cantidad', 1))
    
    if cantidad > producto.stock:
        flash(f'Solo hay {producto.stock} unidades disponibles', 'warning')
        return redirect(url_for('shop.producto_detalle', id=producto_id))
    
    carrito = obtener_carrito()
    
    if str(producto_id) in carrito:
        nueva_cantidad = carrito[str(producto_id)]['cantidad'] + cantidad
        if nueva_cantidad > producto.stock:
            flash(f'Solo hay {producto.stock} unidades disponibles', 'warning')
            return redirect(url_for('shop.producto_detalle', id=producto_id))
        carrito[str(producto_id)]['cantidad'] = nueva_cantidad
    else:
        carrito[str(producto_id)] = {
            'nombre': producto.nombre,
            'precio': float(producto.precio),
            'cantidad': cantidad,
            'imagen': producto.imagenes[0].url if producto.imagenes else None,
            'stock': producto.stock
        }
    
    guardar_carrito(carrito)
    flash(f'"{producto.nombre}" agregado al carrito', 'success')
    return redirect(url_for('shop.ver_carrito'))


@shop_bp.route('/carrito/actualizar/<int:producto_id>', methods=['POST'])
@csrf.exempt
def actualizar_carrito(producto_id):
    """Actualizar la cantidad de un producto en el carrito"""
    producto = Producto.query.get_or_404(producto_id)
    carrito = obtener_carrito()
    
    if str(producto_id) not in carrito:
        flash('Producto no encontrado en el carrito', 'danger')
        return redirect(url_for('shop.ver_carrito'))
    
    nueva_cantidad = int(request.form.get('cantidad', 1))
    
    if nueva_cantidad <= 0:
        del carrito[str(producto_id)]
        flash(f'"{producto.nombre}" eliminado del carrito', 'info')
    elif nueva_cantidad > producto.stock:
        flash(f'Solo hay {producto.stock} unidades disponibles', 'warning')
        return redirect(url_for('shop.ver_carrito'))
    else:
        carrito[str(producto_id)]['cantidad'] = nueva_cantidad
        flash(f'Cantidad actualizada para "{producto.nombre}"', 'success')
    
    guardar_carrito(carrito)
    return redirect(url_for('shop.ver_carrito'))


@shop_bp.route('/carrito/eliminar/<int:producto_id>')
def eliminar_del_carrito(producto_id):
    """Eliminar un producto del carrito"""
    carrito = obtener_carrito()
    
    if str(producto_id) in carrito:
        nombre = carrito[str(producto_id)]['nombre']
        del carrito[str(producto_id)]
        guardar_carrito(carrito)
        flash(f'"{nombre}" eliminado del carrito', 'info')
    else:
        flash('Producto no encontrado en el carrito', 'danger')
    
    return redirect(url_for('shop.ver_carrito'))


@shop_bp.route('/carrito/vaciar')
def vaciar_carrito():
    """Vaciar todo el carrito"""
    session.pop('carrito', None)
    flash('Carrito vaciado', 'info')
    return redirect(url_for('shop.ver_carrito'))


@shop_bp.route('/carrito/cantidad')
def cantidad_carrito():
    """API para obtener la cantidad de productos en el carrito"""
    carrito = obtener_carrito()
    cantidad = sum(item['cantidad'] for item in carrito.values())
    return jsonify({'cantidad': cantidad})


# ==================== CHECKOUT ====================

def generar_codigo_pedido():
    """Generar código único de pedido (ej: #F360-ABC123)"""
    letras = ''.join(random.choices(string.ascii_uppercase, k=6))
    return f'#F360-{letras}'


@shop_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Página de finalizar compra"""
    carrito = obtener_carrito()
    
    if not carrito:
        flash('Tu carrito está vacío', 'warning')
        return redirect(url_for('shop.ver_carrito'))
    
    form = CheckoutForm()
    total = calcular_total(carrito)
    
    if form.validate_on_submit():
        pedido = Pedido(
            codigo=generar_codigo_pedido(),
            total=total,
            direccion_envio=form.direccion.data,
            telefono_contacto=form.telefono.data,
            notas=form.notas.data,
            user_id=current_user.id,
            estado='pendiente'
        )
        db.session.add(pedido)
        db.session.flush()
        
        for producto_id, item in carrito.items():
            detalle = DetallePedido(
                pedido_id=pedido.id,
                producto_id=int(producto_id),
                cantidad=item['cantidad'],
                precio_unitario=item['precio'],
                subtotal=item['precio'] * item['cantidad']
            )
            db.session.add(detalle)
            
            producto = Producto.query.get(int(producto_id))
            if producto:
                producto.stock -= item['cantidad']
        
        db.session.commit()
        session.pop('carrito', None)
        
        flash(f'¡Pedido #{pedido.codigo} confirmado!', 'success')
        return redirect(url_for('shop.confirmacion', pedido_id=pedido.id))
    
    return render_template('shop/checkout.html', 
                         form=form, 
                         carrito=carrito, 
                         total=total)


@shop_bp.route('/confirmacion/<int:pedido_id>')
@login_required
def confirmacion(pedido_id):
    """Página de confirmación del pedido"""
    pedido = Pedido.query.get_or_404(pedido_id)
    
    if pedido.user_id != current_user.id and not current_user.is_admin():
        flash('No tienes permiso para ver este pedido', 'danger')
        return redirect(url_for('shop.index'))
    
    return render_template('shop/confirmacion.html', pedido=pedido)


# ==================== HISTORIAL DE PEDIDOS ====================

@shop_bp.route('/mis-pedidos')
@login_required
def mis_pedidos():
    """Ver el historial de pedidos del cliente"""
    pedidos = Pedido.query.filter_by(user_id=current_user.id).order_by(Pedido.created_at.desc()).all()
    return render_template('shop/mis_pedidos.html', pedidos=pedidos)


@shop_bp.route('/pedido/<int:pedido_id>')
@login_required
def detalle_pedido(pedido_id):
    """Ver detalle de un pedido específico"""
    pedido = Pedido.query.get_or_404(pedido_id)
    
    if pedido.user_id != current_user.id and not current_user.is_admin():
        flash('No tienes permiso para ver este pedido', 'danger')
        return redirect(url_for('shop.index'))
    
    return render_template('shop/detalle_pedido.html', pedido=pedido)