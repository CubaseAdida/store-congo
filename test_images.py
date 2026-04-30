from app import app, db
from models import Store, Product
with app.app_context():
    store = Store.query.first()
    print(f"Store '{store.name}' image: '{store.image}'")
    for p in store.products:
        print(f"Product '{p.name}' image: '{p.image}' (stock: {p.stock})")
    print("Product images in DB:", [p.image for p in Product.query.all() if p.image])
