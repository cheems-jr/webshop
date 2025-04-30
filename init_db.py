from app import app, db
from app import Category, Product

with app.app_context():
    db.drop_all()
    db.create_all()

    if not Category.query.first():
        electronics = Category(name = 'Electronics')
        clothing = Category(name = 'Clothing')  

        db.session.add_all([
            electronics,
            clothing,
            Product(name = 'Wireless Headphones', price = 299.99, category = electronics, stock = 20),
            Product(name = 'Tshirt', price = 19.99, category = clothing, stock = 3),
        ])
        db.session.commit()