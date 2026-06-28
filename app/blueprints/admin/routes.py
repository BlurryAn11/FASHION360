from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import func
from . import admin_bp
from .forms import CategoriaForm, MarcaForm, ProductoForm, ImagenForm
from app.models import User, Categoria, Marca, Producto, Pedido, Imagen, DetallePedido
from app.extensions import db
from app.utils.decorators import role_required
from datetime import datetime
import os
from werkzeug.utils import secure_filename

# ===== FUNCIÓN PARA GUARDAR IMÁGENES =====
def guardar_imagen(archivo, producto_id):
    nombre_original = secure_filename(archivo.filename)
    nombre_unico = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{nombre_original}"
    
    carpeta = os.path.join(current_app.config['UPLOAD_FOLDER'], 'productos')
    os.makedirs(carpeta, exist_ok=True)
    
    ruta_completa = os.path.join(carpeta, nombre_unico)
    archivo.save(ruta_completa)
    
    url_guardar = f'/uploads/productos/{nombre_unico}'
    
    nueva_imagen = Imagen(
        url=url_guardar,
        producto_id=producto_id,
        es_principal=False
    )
    db.session.add(nueva_imagen)
    db.session.commit()
    
    return nueva_imagen

# ==================== DASHBOARD ====================
@admin_bp.route('/')
@login_required
@role_required('admin')
def dashboard():
    total_usuarios = User.query.count()
    total_productos = Producto.query.count()
    total_categorias = Categoria.query.count()
    total_marcas = Marca.query.count()
    total_pedidos = Pedido.query.count()
    
    total_ventas = db.session.query(func.sum(Pedido.total)).scalar() or 0
    ultimos_pedidos = Pedido.query.order_by(Pedido.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_usuarios=total_usuarios,
                         total_productos=total_productos,
                         total_categorias=total_categorias,
                         total_marcas=total_marcas,
                         total_pedidos=total_pedidos,
                         total_ventas=total_ventas,
                         ultimos_pedidos=ultimos_pedidos)

# ==================== CATEGORÍAS ====================
@admin_bp.route('/categorias')
@login_required
@role_required('admin')
def categorias():
    categorias = Categoria.query.order_by(Categoria.nombre).all()
    return render_template('admin/categorias/index.html', categorias=categorias)

@admin_bp.route('/categorias/crear', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def crear_categoria():
    form = CategoriaForm()
    if form.validate_on_submit():
        if Categoria.query.filter_by(nombre=form.nombre.data).first():
            flash('Ya existe una categoría con ese nombre', 'danger')
            return render_template('admin/categorias/crear.html', form=form)
        
        categoria = Categoria(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data
        )
        db.session.add(categoria)
        db.session.commit()
        flash('Categoría creada exitosamente', 'success')
        return redirect(url_for('admin.categorias'))
    
    return render_template('admin/categorias/crear.html', form=form)

@admin_bp.route('/categorias/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def editar_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    form = CategoriaForm(obj=categoria)
    
    if form.validate_on_submit():
        if Categoria.query.filter(Categoria.nombre == form.nombre.data, Categoria.id != id).first():
            flash('Ya existe otra categoría con ese nombre', 'danger')
            return render_template('admin/categorias/editar.html', form=form, categoria=categoria)
        
        categoria.nombre = form.nombre.data
        categoria.descripcion = form.descripcion.data
        db.session.commit()
        flash('Categoría actualizada', 'success')
        return redirect(url_for('admin.categorias'))
    
    return render_template('admin/categorias/editar.html', form=form, categoria=categoria)

# ==================== MARCAS ====================
@admin_bp.route('/marcas')
@login_required
@role_required('admin')
def marcas():
    marcas = Marca.query.order_by(Marca.nombre).all()
    return render_template('admin/marcas/index.html', marcas=marcas)

@admin_bp.route('/marcas/crear', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def crear_marca():
    form = MarcaForm()
    if form.validate_on_submit():
        if Marca.query.filter_by(nombre=form.nombre.data).first():
            flash('Ya existe una marca con ese nombre', 'danger')
            return render_template('admin/marcas/crear.html', form=form)
        
        marca = Marca(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data
        )
        db.session.add(marca)
        db.session.commit()
        flash('Marca creada exitosamente', 'success')
        return redirect(url_for('admin.marcas'))
    
    return render_template('admin/marcas/crear.html', form=form)

@admin_bp.route('/marcas/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def editar_marca(id):
    marca = Marca.query.get_or_404(id)
    form = MarcaForm(obj=marca)
    
    if form.validate_on_submit():
        if Marca.query.filter(Marca.nombre == form.nombre.data, Marca.id != id).first():
            flash('Ya existe otra marca con ese nombre', 'danger')
            return render_template('admin/marcas/editar.html', form=form, marca=marca)
        
        marca.nombre = form.nombre.data
        marca.descripcion = form.descripcion.data
        db.session.commit()
        flash('Marca actualizada exitosamente', 'success')
        return redirect(url_for('admin.marcas'))
    
    return render_template('admin/marcas/editar.html', form=form, marca=marca)

# ==================== PRODUCTOS ====================
@admin_bp.route('/productos')
@login_required
@role_required('admin')
def productos():
    productos = Producto.query.order_by(Producto.created_at.desc()).all()
    return render_template('admin/productos/index.html', productos=productos)

@admin_bp.route('/productos/crear', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def crear_producto():
    form = ProductoForm()
    
    form.categoria_id.choices = [(c.id, c.nombre) for c in Categoria.query.filter_by(activo=True).all()]
    form.marca_id.choices = [(m.id, m.nombre) for m in Marca.query.filter_by(activo=True).all()]
    
    if form.validate_on_submit():
        producto = Producto(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            precio=form.precio.data,
            stock=form.stock.data,
            categoria_id=form.categoria_id.data,
            marca_id=form.marca_id.data,
            destacado=form.destacado.data
        )
        db.session.add(producto)
        db.session.commit()
        flash('Producto creado exitosamente', 'success')
        return redirect(url_for('admin.productos'))
    
    return render_template('admin/productos/crear.html', form=form)

@admin_bp.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def editar_producto(id):
    producto = Producto.query.get_or_404(id)
    form = ProductoForm(obj=producto)
    
    form.categoria_id.choices = [(c.id, c.nombre) for c in Categoria.query.filter_by(activo=True).all()]
    form.marca_id.choices = [(m.id, m.nombre) for m in Marca.query.filter_by(activo=True).all()]
    
    if form.validate_on_submit():
        producto.nombre = form.nombre.data
        producto.descripcion = form.descripcion.data
        producto.precio = form.precio.data
        producto.stock = form.stock.data
        producto.categoria_id = form.categoria_id.data
        producto.marca_id = form.marca_id.data
        producto.destacado = form.destacado.data
        db.session.commit()
        flash('Producto actualizado exitosamente', 'success')
        return redirect(url_for('admin.productos'))
    
    return render_template('admin/productos/editar.html', form=form, producto=producto)

# ==================== ELIMINAR ====================

@admin_bp.route('/categorias/eliminar/<int:id>')
@login_required
@role_required('admin')
def eliminar_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    
    total_productos = db.session.query(func.count(Producto.id)).filter(Producto.categoria_id == id).scalar()
    
    if total_productos > 0:
        flash(f'No se puede eliminar la categoría "{categoria.nombre}" porque tiene {total_productos} productos asociados', 'danger')
        return redirect(url_for('admin.categorias'))
    
    nombre = categoria.nombre
    db.session.delete(categoria)
    db.session.commit()
    flash(f'Categoría "{nombre}" eliminada permanentemente', 'success')
    return redirect(url_for('admin.categorias'))

@admin_bp.route('/marcas/eliminar/<int:id>')
@login_required
@role_required('admin')
def eliminar_marca(id):
    marca = Marca.query.get_or_404(id)
    
    total_productos = db.session.query(func.count(Producto.id)).filter(Producto.marca_id == id).scalar()
    
    if total_productos > 0:
        flash(f'No se puede eliminar la marca "{marca.nombre}" porque tiene {total_productos} productos asociados', 'danger')
        return redirect(url_for('admin.marcas'))
    
    nombre = marca.nombre
    db.session.delete(marca)
    db.session.commit()
    flash(f'Marca "{nombre}" eliminada permanentemente', 'success')
    return redirect(url_for('admin.marcas'))

@admin_bp.route('/productos/eliminar/<int:id>')
@login_required
@role_required('admin')
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    
    total_pedidos = db.session.query(func.count(DetallePedido.id)).filter(DetallePedido.producto_id == id).scalar()
    
    if total_pedidos > 0:
        flash(f'No se puede eliminar el producto "{producto.nombre}" porque tiene {total_pedidos} pedidos asociados', 'danger')
        return redirect(url_for('admin.productos'))
    
    nombre = producto.nombre
    db.session.delete(producto)
    db.session.commit()
    flash(f'Producto "{nombre}" eliminado permanentemente', 'success')
    return redirect(url_for('admin.productos'))

# ==================== IMÁGENES ====================
@admin_bp.route('/productos/<int:id>/imagenes', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def gestionar_imagenes(id):
    from .forms import ImagenForm
    
    producto = Producto.query.get_or_404(id)
    form = ImagenForm()
    
    if form.validate_on_submit():
        try:
            imagen = guardar_imagen(form.imagen.data, producto.id)
            
            if form.es_principal.data:
                Imagen.query.filter_by(producto_id=producto.id).update({'es_principal': False})
                imagen.es_principal = True
                db.session.commit()
            
            flash('Imagen subida exitosamente', 'success')
        except Exception as e:
            flash(f'Error al subir la imagen: {str(e)}', 'danger')
        return redirect(url_for('admin.gestionar_imagenes', id=producto.id))
    
    imagenes = Imagen.query.filter_by(producto_id=producto.id).order_by(Imagen.es_principal.desc()).all()
    
    return render_template('admin/productos/imagenes.html', 
                         producto=producto, 
                         imagenes=imagenes,
                         form=form)

@admin_bp.route('/productos/imagenes/eliminar/<int:id>')
@login_required
@role_required('admin')
def eliminar_imagen(id):
    imagen = Imagen.query.get_or_404(id)
    producto_id = imagen.producto_id
    
    try:
        ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], 'productos', os.path.basename(imagen.url))
        if os.path.exists(ruta):
            os.remove(ruta)
    except:
        pass
    
    db.session.delete(imagen)
    db.session.commit()
    flash('Imagen eliminada', 'success')
    return redirect(url_for('admin.gestionar_imagenes', id=producto_id))

@admin_bp.route('/productos/imagenes/principal/<int:id>')
@login_required
@role_required('admin')
def marcar_principal(id):
    imagen = Imagen.query.get_or_404(id)
    producto_id = imagen.producto_id
    
    Imagen.query.filter_by(producto_id=producto_id).update({'es_principal': False})
    imagen.es_principal = True
    db.session.commit()
    
    flash('Imagen marcada como principal', 'success')
    return redirect(url_for('admin.gestionar_imagenes', id=producto_id))

# ==================== GESTIÓN DE PEDIDOS (ADMIN) ====================

@admin_bp.route('/pedidos')
@login_required
@role_required('admin')
def listar_pedidos():
    pedidos = Pedido.query.order_by(Pedido.created_at.desc()).all()
    return render_template('admin/pedidos/index.html', pedidos=pedidos)

@admin_bp.route('/pedidos/<int:pedido_id>')
@login_required
@role_required('admin')
def ver_pedido(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    return render_template('admin/pedidos/detalle.html', pedido=pedido)

@admin_bp.route('/pedidos/cambiar-estado/<int:pedido_id>/<string:estado>')
@login_required
@role_required('admin')
def cambiar_estado_pedido(pedido_id, estado):
    pedido = Pedido.query.get_or_404(pedido_id)
    estados_validos = ['pendiente', 'confirmado', 'enviado', 'entregado', 'cancelado']
    
    if estado not in estados_validos:
        flash('Estado no válido', 'danger')
        return redirect(url_for('admin.ver_pedido', pedido_id=pedido_id))
    
    pedido.estado = estado
    db.session.commit()
    flash(f'Pedido {pedido.codigo} actualizado a: {estado}', 'success')
    return redirect(url_for('admin.ver_pedido', pedido_id=pedido_id))