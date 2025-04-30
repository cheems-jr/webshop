from flask import Flask, render_template, redirect, request, session # type: ignore
from flask_sqlalchemy import SQLAlchemy # type: ignore
from dotenv import load_dotenv # type: ignore
import os
from datetime import datetime, timezone
import uuid

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@"
    f"{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    price = db.Column(db.Float, nullable = False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(100))
    stock = db.Column(db.Integer, default = 0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    category = db.relationship('Category', back_populates='products')

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), unique = True, nullable = False)

    products = db.relationship('Product', back_populates='category')

class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key = True)
    user_session = db.Column(db.String(100), )
    created_at = db.Column(db.DateTime, default = datetime.now(timezone.utc))

    cart_items = db.relationship('CartItem', back_populates='cart', cascade='all, delete-orphan')

class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key = True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable = False)
    quantity = db.Column(db.Integer, default=1)

    item = db.relationship('Product')
    cart = db.relationship('Cart', back_populates='cart_items')

    

def cart_create_or_get():
    if 'cart_id' not in session:
        cart = Cart(user_session = str(uuid.uuid4()))
        db.session.add(cart)
        db.session.commit()
        session['cart_id'] = cart.id
    return Cart.query.get(session['cart_id'])

def cart_get_items():
    cart = cart_create_or_get()
    return cart.cart_items

def cart_add_item(product_id, item_quantity):
    cart = cart_create_or_get()
    existing_item = next((item for item in cart.cart_items if item.id == product_id), None)

    if existing_item:
        existing_item.quantity += item_quantity
    else:
        new_item = CartItem(
            cart_id = cart.id,
            item_id = product_id,
            quantity = item_quantity
        )
        db.session.add(new_item)
    db.session.commit()


@app.route('/add_to_cart', methods = ['POST'])
def add_to_cart_route():
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))
    cart_add_item(product_id, quantity)
    return redirect(request.referrer or '/')

@app.route('/cart')
def cart_get_items_route():
    items = cart_get_items()
    total = sum(item.item.price * item.quantity for item in items)
    return render_template('cart.html', items = items, total = total)

@app.route('/remove_from_cart/<int:item_id>')
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect('/cart')


@app.route('/')
def homepage():
    featured = Product.query.order_by(db.func.random()).limit(3).all()
    return render_template('index.html', featured_products = featured)


@app.route('/products')
def product_list():
    products = Product.query.all()
    return render_template('products.html', products = products)


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product = product)

@app.context_processor
def inject_cart_count():
    if 'cart_id' in session:
        cart = Cart.query.get(session['cart_id'])
        return {'cart_count': len(cart.cart_items) if cart else 0}
    return {'cart_count': 0}

if __name__ == '__main__':
    app.run(debug=True)