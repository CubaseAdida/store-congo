from flask import Flask, render_template, flash, redirect, url_for, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
from config import Config
from models import db, User, Store, Product, Comment, Offer, News, Job
from forms import LoginForm, StoreForm, ProductForm, OfferForm, NewsForm, JobForm
from sqlalchemy.exc import OperationalError
from flask import send_from_directory

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'store-congo-secret-2024-change-in-production'
app.config['UPLOAD_FOLDER'] = 'static/uploads/stores'
app.config['PRODUCT_UPLOAD_FOLDER'] = 'static/uploads/products'
app.config['OFFRE_UPLOAD_FOLDER'] = 'static/uploads/offres'
app.config['NEWS_UPLOAD_FOLDER'] = 'static/uploads/news'
app.config['JOBS_UPLOAD_FOLDER'] = 'static/uploads/jobs'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
if not os.path.exists(app.config['PRODUCT_UPLOAD_FOLDER']):
    os.makedirs(app.config['PRODUCT_UPLOAD_FOLDER'], exist_ok=True)
if not os.path.exists(app.config['OFFRE_UPLOAD_FOLDER']):
    os.makedirs(app.config['OFFRE_UPLOAD_FOLDER'], exist_ok=True)
if not os.path.exists(app.config['NEWS_UPLOAD_FOLDER']):
    os.makedirs(app.config['NEWS_UPLOAD_FOLDER'], exist_ok=True)
if not os.path.exists(app.config['JOBS_UPLOAD_FOLDER']):
    os.makedirs(app.config['JOBS_UPLOAD_FOLDER'], exist_ok=True)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.errorhandler(OperationalError)
def handle_db_error(error):
    flash('Erreur base de données temporaire. Réessayez.')
    return 'Erreur serveur', 500

@app.errorhandler(500)
def internal_error(error):
    flash('Erreur interne. Vérifiez la console.')
    return render_template('index.html', stores=[]), 500

@app.route('/')
def index():
    query = request.args.get('q', '').strip()
    if query:
        return redirect(url_for('search', q=query))
    try:
        stores = Store.query.all()
        return render_template('index.html', stores=stores)
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur DB: {str(e)[:100]}')
        return render_template('index.html', stores=[])

@app.route('/search')
def search():
    query = request.args.get('q', '').strip().lower()
    if not query:
        return redirect(url_for('index'))
    
    stores = Store.query.filter(Store.name.ilike(f'%{query}%')).all() if query else []
    products = Product.query.filter(Product.name.ilike(f'%{query}%')).all() if query else []
    
    return render_template('search_results.html', query=query, stores=stores, products=products)

@app.route('/offres')
def offres():
    try:
        offres = Offer.query.options(db.joinedload(Offer.store)).all()
        stores = Store.query.all()
        return render_template('offres.html', offres=offres, stores=stores)
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur offres: {str(e)}')
        return render_template('offres.html', offres=[], stores=[])

@app.route('/news')
def news():
    news_list = News.query.order_by(News.created_at.desc()).all()
    return render_template('news.html', news=news_list)

@app.route('/admin/add_offre_emploi', methods=['GET', 'POST'])
@login_required
def add_offre_emploi():
    form = JobForm()
    if form.validate_on_submit():
        try:
            f = form.image.data
            filename = None
            if f:
                import time
                timestamp = int(time.time())
                name, ext = os.path.splitext(secure_filename(f.filename))
                filename = f"{name}_{timestamp}{ext}"
                path = os.path.join(app.config['JOBS_UPLOAD_FOLDER'], filename)
                jobs_dir = app.config['JOBS_UPLOAD_FOLDER']
                os.makedirs(jobs_dir, exist_ok=True)
                f.save(path)

            job = Job(
                title=form.title.data.strip(),
                description=form.description.data.strip(),
                location=form.location.data.strip(),
                type=form.type.data,
                salary=form.salary.data.strip(),
                whatsapp=form.whatsapp.data or None,
                image=filename
            )
            db.session.add(job)
            db.session.commit()
            flash("✅ Offre d'emploi '{}' publiée!".format(job.title))
            return redirect(url_for('admin_offres_emploi'))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Erreur: {str(e)}')
    return render_template('add_offre_emploi.html', form=form)

@app.route('/offres-emploi')
def offres_emploi():
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    return render_template('offres_emploi.html', jobs=jobs)

@app.route('/admin/offres_emploi')
@login_required
def admin_offres_emploi():
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    return render_template('admin_offres_emploi.html', jobs=jobs)

@app.route('/admin/delete_job/<int:job_id>', methods=['POST'])
@login_required
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    job_title = job.title
    if job.image:
        image_path = os.path.join(app.config['JOBS_UPLOAD_FOLDER'], job.image)
        if os.path.exists(image_path):
            os.remove(image_path)
    db.session.delete(job)
    db.session.commit()
    flash(f'✅ Offre "{job_title}" supprimée!')
    return redirect(url_for('admin_offres_emploi'))

@app.route('/admin/partners', methods=['GET', 'POST'])
@login_required
def admin_partners():
    partners_dir = 'static/partners'
    os.makedirs(partners_dir, exist_ok=True)
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'upload':
            names = ['logo1', 'logo2', 'logo3']
            for name in names:
                f = request.files.get(name)
                if f and f.filename:
                    filename = secure_filename(f.filename)
                    if '.' in filename:
                        base_name, ext = filename.rsplit('.', 1)
                        preferred_ext = '.svg' if ext.lower() == 'svg' else '.png'
                        filename = f"{name}{preferred_ext}"
                    path = os.path.join(partners_dir, filename)
                    f.save(path)
                    flash(f'✅ {filename} uploadé!')
            flash('✅ Logos mis à jour!')
        elif action == 'delete':
            filename = request.form.get('filename')
            if filename:
                path = os.path.join(partners_dir, filename)
                if os.path.exists(path):
                    os.remove(path)
                    flash(f'✅ {filename} supprimé!')
                else:
                    flash(f'❌ {filename} non trouvé')
    
    # List current logos
    partners = [f for f in os.listdir(partners_dir) if f.startswith('logo') and f.lower().endswith(('.png', '.svg', '.jpg', '.jpeg'))]
    
    return render_template('admin_partners.html', partners=partners)

@app.route('/upload_partner', methods=['POST'])
def upload_partner():
    os.makedirs('static/partners', exist_ok=True)
    names = ['logo1', 'logo2', 'logo3']
    for name in names:
        f = request.files.get(name)
        if f and f.filename:
            filename = secure_filename(f.filename)
            if '.' in filename:
                name, ext = filename.rsplit('.', 1)
                filename = f"{name}.svg" if ext.lower() == 'svg' else f"{name}.png"
            path = os.path.join('static/partners', filename)
            f.save(path)
            flash(f'✅ {filename} uploadé')
    flash('✅ Logos partenaires mis à jour!')
    return redirect(request.referrer or url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Identifiants invalides')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/admin/add_news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        try:
            filenames = []
            for i, f in enumerate([form.image1.data, form.image2.data, form.image3.data], 1):
                if f:
                    import time
                    timestamp = int(time.time())
                    name, ext = os.path.splitext(secure_filename(f.filename))
                    filename = f"news_{i}_{name}_{timestamp}{ext}"
                    path = os.path.join(app.config['NEWS_UPLOAD_FOLDER'], filename)
                    f.save(path)
                    filenames.append(filename)
            news = News(
                title=form.title.data.strip(),
                content=form.content.data.strip(),
                image1=filenames[0] if len(filenames) > 0 else None,
                image2=filenames[1] if len(filenames) > 1 else None,
                image3=filenames[2] if len(filenames) > 2 else None
            )
            db.session.add(news)
            db.session.commit()
            flash(f'✅ Actualité "{news.title}" publiée!')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Erreur: {str(e)}')
    return render_template('add_news.html', form=form)

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    cart_items = session.get('cart', [])
    
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        if product_id:
            cart_items = [item for item in cart_items if str(item['id']) != product_id]
            session['cart'] = cart_items
            session.modified = True
            flash('✅ Article supprimé du panier!')
            return redirect(url_for('cart'))
    
    valid_items = []
    store_groups = {}
    grand_total = 0
    
    for item in cart_items:
        product = Product.query.get(item['id'])
        if product:
            valid_items.append(item)
            if product.store:
                store_id = product.store.id
                if store_id not in store_groups:
                    store_groups[store_id] = []
                item_copy = item.copy()
                item_copy.update({
                    'store_name': product.store.name,
                    'whatsapp': product.store.whatsapp or ''
                })
                store_groups[store_id].append(item_copy)
            grand_total += item['price'] * item['quantity']
    
    session['cart'] = valid_items
    session.modified = True
    
    return render_template('cart.html', 
                         cart_items=valid_items, 
                         store_groups=store_groups, 
                         grand_total=grand_total)

@app.route('/update_cart', methods=['POST'])
def update_cart():
    product_id = request.form['product_id']
    new_qty = int(request.form['quantity'])
    
    cart_items = session.get('cart', [])
    for item in cart_items:
        if item['id'] == int(product_id):
            item['quantity'] = new_qty
            if new_qty <= 0:
                cart_items.remove(item)
            break
    
    session['cart'] = cart_items
    session.modified = True
    return 'OK'

@app.route('/cart_count')
def cart_count():
    count = len(session.get('cart', []))
    return {'count': count}

@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    session['cart'] = []
    session.modified = True
    return 'OK'

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    cart_items = session.get('cart', [])
    for item in cart_items:
        if item['id'] == product_id:
            item['quantity'] += 1
            break
    else:
        cart_items.append({
            'id': product_id,
            'name': product.name,
            'price': float(product.price),
            'image': product.image,
            'quantity': 1
        })
    session['cart'] = cart_items
    session.modified = True
    flash(f'{product.name} ajouté au panier !')
    return redirect(request.referrer or url_for('index'))

@app.route('/add_store', methods=['GET', 'POST'])
@login_required
def add_store():
    form = StoreForm()
    if form.validate_on_submit():
        try:
            f = form.image.data
            filename = None
            if f:
                filename = secure_filename(f.filename)
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                store_dir = app.config['UPLOAD_FOLDER']
                os.makedirs(store_dir, exist_ok=True)
                f.save(path)
            store = Store(
                name=form.name.data,
                description=form.description.data,
                whatsapp=form.whatsapp.data or None,
                image=filename
            )
            db.session.add(store)
            db.session.flush()
            count_avant = Store.query.count()
            db.session.commit()
            count_apres = Store.query.count()
            flash(f'✅ Boutique ajoutée! DEBUG: count avant={count_avant}, après={count_apres}, ID={store.id}')
            print(f"DEBUG ADD_STORE: count avant={count_avant}, après={count_apres}, store={store.name}")
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Erreur création boutique: {str(e)}')
    return render_template('add_store.html', form=form)

@app.route('/add_offre', methods=['GET', 'POST'])
@login_required
def add_offre():
    form = OfferForm()
    if form.validate_on_submit():
        try:
            store = Store.query.get_or_404(form.store_id.data)
            f = form.image.data
            filename = None
            if f:
                import time
                timestamp = int(time.time())
                name, ext = os.path.splitext(secure_filename(f.filename))
                filename = f"{name}_{timestamp}{ext}"
                offre_path = os.path.join(app.config['OFFRE_UPLOAD_FOLDER'], filename)
                offre_dir = app.config['OFFRE_UPLOAD_FOLDER']
                os.makedirs(offre_dir, exist_ok=True)
                f.save(offre_path)
            offer = Offer(
                title=form.title.data.strip(),
                description=form.description.data.strip() or None,
                discount=form.discount.data,
                image=filename,
                store_id=form.store_id.data
            )
            db.session.add(offer)
            db.session.commit()
            flash(f'✅ Offre ajoutée pour {store.name}! ID={offer.id} | {offer.discount}% off')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Erreur offre: {str(e)}')
    return render_template('add_offre.html', form=form)

@app.route('/stores')
@login_required
def stores():
    stores = []
    try:
        stores = Store.query.options(db.joinedload(Store.products), db.joinedload(Store.comments)).all()
        count = len(stores)
        print(f"DEBUG STORES FIXED: {count} boutiques loaded")
        if count == 0:
            flash('⚠️ DEBUG: Aucune boutique trouvée.')
        else:
            flash(f'✅ {count} boutique(s) affichée(s).')
    except Exception as e:
        print(f"ERROR STORES: {str(e)}")
        flash(f'❌ Erreur: {str(e)[:100]}')
    return render_template('stores.html', stores=stores)

@app.route('/store/<int:store_id>')
@login_required
def store_detail(store_id):
    store = Store.query.get_or_404(store_id)
    products = Product.query.filter_by(store_id=store_id).all()
    form = ProductForm()
    return render_template('store_detail.html', store=store, products=products, form=form)

@app.route('/public_store/<int:store_id>')
def public_store(store_id):
    try:
        store = Store.query.get_or_404(store_id)
        query = request.args.get('q', '').strip().lower()
        if query:
            products = Product.query.filter_by(store_id=store_id).filter(Product.name.ilike(f'%{query}%')).all()
        else:
            products = Product.query.filter_by(store_id=store_id).all()
        comments = Comment.query.filter_by(store_id=store_id).order_by(Comment.created_at.desc()).all()
        return render_template('store_public.html', store=store, products=products, comments=comments, query=query)
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur boutique: {str(e)}')
        return redirect(url_for('index'))

@app.route('/store/<int:store_id>/search')
def store_search(store_id):
    store = Store.query.get_or_404(store_id)
    query = request.args.get('q', '').strip().lower()
    if not query:
        return redirect(url_for('public_store', store_id=store.id))
    products = Product.query.filter_by(store_id=store.id).filter(Product.name.ilike(f'%{query}%')).all()
    comments = Comment.query.filter_by(store_id=store.id).order_by(Comment.created_at.desc()).all()
    return render_template('store_public.html', store=store, products=products, comments=comments, query=query)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.options(db.joinedload(Product.store)).get_or_404(product_id)
    store = product.store
    return render_template('product_detail_simple.html', product=product, store=store)

@app.route('/store/<int:store_id>/comment', methods=['POST'])
def add_comment(store_id):
    try:
        name = request.form.get('name', '').strip()
        comment_text = request.form.get('comment', '').strip()
        
        if not name or len(name) < 2 or not comment_text or len(comment_text) < 5:
            flash('❌ Nom (2+ chars) et commentaire (5+ chars) requis!')
            return redirect(url_for('public_store', store_id=store_id))
        
        new_comment = Comment(
            store_id=store_id,
            name=name[:100],
            comment=comment_text[:500]
        )
        db.session.add(new_comment)
        db.session.commit()
        flash('✅ Commentaire ajouté ! Merci !')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Erreur ajout commentaire: {str(e)}')
    
    return redirect(url_for('public_store', store_id=store_id))

@app.route('/admin/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    store = comment.store
    db.session.delete(comment)
    db.session.commit()
    flash(f'✅ Commentaire supprimé de {store.name}')
    return redirect(url_for('stores'))

@app.route('/store/<int:store_id>/add_product', methods=['POST'])
@login_required
def add_product(store_id):
    form = ProductForm()
    print(f"DEBUG FORM DATA: name='{form.name.data}', price={form.price.data}, stock={form.stock.data}, image={form.image.data}")
    print(f"DEBUG ERRORS: {form.errors}")
    
    product_count_before = Product.query.filter_by(store_id=store_id).count()
    print(f"DEBUG ADD_PRODUCT store_id={store_id}: {product_count_before} produits avant")
    
    if form.validate_on_submit():
        image_filename = None
        try:
            f = form.image.data
            if f:
                flash(f'✅ Image OK: {f.filename}')
                import time
                timestamp = int(time.time())
                name, ext = os.path.splitext(secure_filename(f.filename))
                image_filename = f"{name}_{timestamp}{ext}"
                path = os.path.join(app.config['PRODUCT_UPLOAD_FOLDER'], image_filename)
                print(f"SAVING PRODUCT IMAGE to: {os.path.abspath(path)}")
                product_dir = app.config['PRODUCT_UPLOAD_FOLDER']
                os.makedirs(product_dir, exist_ok=True)
                f.save(path)
                print(f"SAVED OK: {os.path.exists(path)} size={os.path.getsize(path) if os.path.exists(path) else 0}")

            product = Product(
                name=form.name.data.strip() or 'Sans nom',
                price=float(form.price.data or 0),
                stock=int(form.stock.data or 0),
                image=image_filename,
                store_id=store_id
            )
            db.session.add(product)
            db.session.commit()
            product_count_after = Product.query.filter_by(store_id=store_id).count()
            flash(f'✅ PRODUIT AJOUTÉ ID={product.id}: {product.name} | {product.price}FC | Stock {product.stock} | TOTAL BOUTIQUE: {product_count_after}')
            print(f"DEBUG SUCCESS store_id={store_id}: +1 produit, total {product_count_after}")
            return redirect(url_for('store_detail', store_id=store_id))
        except Exception as db_err:
            db.session.rollback()
            flash(f'❌ ERREUR DB AJOUT PRODUIT: {str(db_err)[:100]} | Produits avant: {product_count_before}')
            print(f"DEBUG DB ERROR: {db_err}")
    else:
        flash(f'❌ FORMULAIRE INVAILDE (produits avant:{product_count_before}). Vérifiez nom, prix (nombre), stock (entier).')
    return redirect(url_for('store_detail', store_id=store_id))


@app.route('/store/<int:store_id>/edit_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(store_id, product_id):
    product = Product.query.get_or_404(product_id)
    if product.store_id != store_id:
        flash('Non autorisé')
        return redirect(url_for('dashboard'))
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        product.name = form.name.data
        product.price = form.price.data
        product.stock = form.stock.data
        db.session.commit()
        flash('Article modifié!')
        return redirect(url_for('store_detail', store_id=store_id))
    return render_template('edit_product.html', form=form, product=product, store_id=store_id)

@app.route('/store/<int:store_id>/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(store_id, product_id):
    product = Product.query.get_or_404(product_id)
    if product.store_id != store_id:
        flash('Non autorisé')
        return redirect(url_for('dashboard'))
    db.session.delete(product)
    db.session.commit()
    flash('Article supprimé!')
    return redirect(url_for('store_detail', store_id=store_id))

@app.route('/admin/store/<int:store_id>/delete', methods=['POST'])
@login_required
def delete_store(store_id):
    store = Store.query.get_or_404(store_id)
    store_name = store.name
    num_products = len(store.products)
    num_comments = len(store.comments)
    db.session.delete(store)
    db.session.commit()
    flash(f'✅ Boutique "{store_name}" supprimée avec {num_products} produits et {num_comments} commentaires.')
    return redirect(url_for('stores'))

@app.route('/uploads/<string:type>/<string:filename>')
def uploaded_file(type, filename):
    from flask import abort
    allowed_types = ['stores', 'products', 'offres', 'news', 'jobs']
    if type not in allowed_types:
        abort(404)
    upload_dir = f'static/uploads/{type}'
    if not os.path.exists(upload_dir):
        abort(404)
    return send_from_directory(upload_dir, filename)

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            # Create new admin user (Muteba328/Muteba328)
            if not User.query.filter_by(username='Muteba328').first():
                new_admin = User(username='Muteba328')
                new_admin.set_password('Muteba328')
                db.session.add(new_admin)
            # Keep old admin for compatibility
            if not User.query.filter_by(username='admin').first():
                admin = User(username='admin')
                admin.set_password('Muteba328')
                db.session.add(admin)
            db.session.commit()
            print('✅ Admin créé: Muteba328 / Muteba328')
            print('✅ DB initialisée correctement - tables créées')
        except Exception as e:
            print(f'❌ Erreur init DB: {e}')
            print('Solution: Vérifiez models.py et relancez')
    app.run(host='0.0.0.0', port=5000, debug=True)
