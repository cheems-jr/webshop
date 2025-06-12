from flask import Flask, render_template, redirect, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy 
from dotenv import load_dotenv 
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
    return cart

@app.route('/cart_summary')
def cart_summary():
    cart_items = cart_get_items()
    return jsonify({
        'cart_count': sum(item.quantity for item in cart_items),
        'subtotal': sum(item.quantity * item.item.price for item in cart_items)
    })


@app.route('/add_to_cart', methods = ['POST'])
def add_to_cart_ajax():
    if request.is_json:
        data = request.json
        product_id = int(data['product_id'])
        quantity = int(data.get('quantity', 1))

        try:
            cart = cart_add_item(product_id, quantity)

            return jsonify({
                'status': 'success',
                'cart_count': sum(item.quantity for item in cart.cart_items),
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 400
    return jsonify({'status': 'error', 'message': 'Invalid request'}), 400

@app.route('/cart')
def cart_get_items_route():
    cart = cart_create_or_get()
    items = CartItem.query.filter_by(cart_id=cart.id).order_by(CartItem.id.asc()).all()
    total = sum(item.item.price * item.quantity for item in items)
    return render_template('cart.html', items = items, total = total)

@app.route('/remove_cart_item', methods = ['POST'])
def remove_cart_item():
    data = request.get_json()
    item = CartItem.query.get(data['item_id'])

    if item:
        cart = item.cart
        print(cart)
        db.session.delete(item)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'grand_total': sum(i.item.price * i.quantity for i in cart.cart_items),
            'is_cart_empty': len(cart.cart_items) == 0 
        })

    return jsonify({'status': 'error', 'message': 'Invalid Request'}), 400

@app.route('/update_cart_item', methods = ['POST'])
def update_cart_item():
    data = request.get_json()
    item = CartItem.query.get(data['item_id'])
    
    if item:
        item.quantity = int(data['quantity'])
        db.session.commit()

        return jsonify({
            'status': 'success',
            'new_total': item.item.price * item.quantity,
            'grand_total': sum(i.item.price * i.quantity for i in item.cart.cart_items),
            'cart_item_id': item.id,
        })

    return jsonify({'status': 'error', 'message': 'invalid_request'}), 400


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

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

if __name__ == '__main__':
    app.run(debug=True)