from flask import Flask, render_template # type: ignore
from flask_sqlalchemy import SQLAlchemy # type: ignore
from dotenv import load_dotenv # type: ignore
import os

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@"
    f"{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)

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




@app.route('/')
def homepage():
    return render_template('index.html', featured_products = products[:2])


products = [
    {"id" : 1, 'name' : 'python t-shirt', 'price' : 24.99},
    {"id" : 2, 'name' : 'flosk mug', 'price' : 19.99},
    {'id' : 3, 'name' : 'chinese treats', 'price' : 2.99}
]

@app.route('/products')
def product_list():
    return render_template('products.html', products = products)


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        return render_template('product_detail.html', product = product)
    return 'Product not found', 404


if __name__ == '__main__':
    app.run(debug=True)