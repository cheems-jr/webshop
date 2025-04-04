from app import app, db
from app import Category, Product

with app.app_context():
    db.create_all()

    if not Category.query.first():
        electronics = Category(name = 'Electronics')
        clothing = Category(name = 'Clothing')

        db.session.add_all([
            electronics,
            clothing,
            Product(name = 'Wireless Headphones', price = 299.99, category = electronics),
            Product(name = 'Tshirt', price = 19.99, category = clothing),
        ])
        db.session.commit()