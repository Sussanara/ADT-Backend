from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db,Admin, User, Product
from flask_cors import CORS
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['ENV'] = 'development'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['JSON_SORT_KEYS'] = False

db.init_app(app)
Migrate(app,db)
CORS(app)

#GET ALL ADMINS
@app.route('/api/admin', methods = ['GET'])
def admin_list():
    if request.method == 'GET':
        admins = Admin.query.all()
        admins = list(map(lambda admin: admin.serialize(),admins))
        return jsonify(admins)

#GET ALL USERS /// POST USER
@app.route('/api/users', methods = ['GET','POST'])
def get_and_post_users_with_products():

    #GET ALL USERS
    if request.method == 'GET':
        users = User.query.all()
        users = list(map(lambda user: user.serialize_with_products(), users))
        return jsonify(users),200
    
    #USER CREATION
    if request.method == 'POST':
        user = User()
        user.email = request.json.get('email')
        user.password = request.json.get('password')
        user.empresa = request.json.get('empresa')
        user.phone = request.json.get('phone')
        user.firstName = request.json.get('firstName')
        user.lastName = request.json.get('lastName')
        user.run = request.json.get('run')

        user.save()
        
        all_users = User.query.all()
        all_users = list(map(lambda user: user.serialize(),all_users))
        return jsonify(all_users),200
    

#GET USER BY ID , EDIT USER, POST PRODUCT , DELETE USER
@app.route('/api/users/<int:id>', methods = ['GET','POST','PUT','DELETE'])
def get_edit_postProduct_user_by_id(id):
    #Get User by ID
    if request.method == 'GET':
        user = User.query.get(id)
        return jsonify(user.serialize()),200
    
    #Edit User
    if request.method == 'PUT':
        new_email = request.json.get('email')
        new_password = request.json.get('password')
        new_empresa = request.json.get('empresa')
        new_phone = request.json.get('phone')
        new_firstName = request.json.get('firstName')
        new_lastName = request.json.get('lastName')
        new_run = request.json.get('run')
        new_is_active = request.json.get('is_active')

        user = User.query.get(id)

        user.email = new_email
        user.password = new_password
        user.empresa = new_empresa
        user.phone = new_phone
        user.firstName = new_firstName
        user.lastName = new_lastName
        user.run = new_run
        user.is_active = new_is_active
        
        user.update()
        users = User.query.all()
        return jsonify(list(map(lambda user: user.serialize(),users))),200

    if request.method == 'DELETE':
        user = User.query.get(id)
        user.delete()
        all_users = User.query.all()
        return jsonify(list(map(lambda user: user.serialize(),all_users)))

    #Post Product
    if request.method == 'POST':
        product = Product()
        product.owner_id = id
        product.name = request.json.get('name')
        product.stock = request.json.get('stock')
        product.sold_stock = request.json.get('sold_stock')
        product.price = request.json.get('price')

        product.save()
        user = User.query.get(id)
        return jsonify(user.serialize_with_products()),200


#GET USER and PRODUCTS by ID
@app.route('/api/users/<int:id>/products', methods = ['GET'])
def get_products_by_user(id):
    if request.method == 'GET':
        user = User.query.get(id)
        return jsonify(user.serialize_with_products()),200
    
    
#GET PRODUCT by ID , AND EDIT PRODUCT by ID , DELETE PRODUCT by ID
@app.route('/api/users/<int:id>/products/<int:product_id>', methods = ['GET','PUT','DELETE'])
def get_product_by_id(id,product_id):
    if request.method == 'GET':
        product = Product.query.get(product_id)
        return jsonify(product.serialize()),200
    
    if request.method == 'PUT':
        new_name = request.json.get('name')
        new_stock = request.json.get('stock')
        new_sold_stock = request.json.get('sold_stock')
        new_price = request.json.get('price')

        product = Product.query.get(product_id)

        product.name = new_name
        product.stock = new_stock
        product.sold_stock = new_sold_stock
        product.price = new_price

        product.update()
        user = User.query.get(id)

        return jsonify(user.serialize_with_products()),200
    
    if request.method == 'DELETE':
        product = Product.query.get(product_id)
        product.delete()
        user = User.query.get(id)
        return jsonify(user.serialize_with_products()),200

#Edit Product by ID
@app.route('/api/users/products/<int:product_id>', methods = ['PUT'])
def edit_product_by_id(product_id):
    if request.method == 'PUT':
        new_name = request.json.get('name')
        new_stock = request.json.get('stock')
        new_sold_stock = request.json.get('sold_stock')
        new_price = request.json.get('price')

        product = Product.query.get(product_id)

        product.name = new_name
        product.stock = new_stock
        product.sold_stock = new_sold_stock
        product.price = new_price

        product.update()

        return jsonify(product.serialize()),200

if __name__ == '__main__':
    app.run()