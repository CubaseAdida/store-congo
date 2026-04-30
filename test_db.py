from app import app
from models import db, Store, Product
with app.app_context():
    print('=== DIAGNOSTIC BASE DONNEES ===')
    print('Nombre magasins:', Store.query.count())
    stores = Store.query.all()
    for i, s in enumerate(stores[:3],1):
        print(f'Magasin {i}: {s.name} - Produits: {[p.name for p in s.products]}')
    print('Total produits:', Product.query.count())
    if Store.query.count() == 0:
        print('🚨 BASE VIDE : Ajoutez un magasin via UI')

