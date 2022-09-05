from itertools import product
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager, create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash
from models import db,Admin, User, Product, UserDecrypted
from flask_cors import CORS
import cloudinary
cloudinary.config( 
  cloud_name = "diyqwze9g", 
  api_key = "287765888235726", 
  api_secret = "pQcrDhyVdmyoPYIrCcuSh3bo4yM" 
)
import cloudinary.uploader
import cloudinary.api
import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['ENV'] = 'development'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['JWT_SECRET_KEY'] = '6c5c61586204fadea58b8be931023960'
app.config['JSON_SORT_KEYS'] = False

db.init_app(app)
Migrate(app,db)
CORS(app)
jwt = JWTManager(app)


#GET ALL ADMINS
@app.route('/api/admin', methods = ['GET','POST'])
def admin_list():
    if request.method == 'GET':
        admins = Admin.query.all()
        admins = list(map(lambda admin: admin.serialize(),admins))
        return jsonify(admins),200

    #Create Admin -> Careful!
    if request.method == 'POST':
        email = request.json.get('email')
        password = request.json.get('password')
        #Comprobacion de Datos...
        if not email: return jsonify({"msg" : "Falta un Email!"}),400
        if not password: return jsonify({"msg" : "Falta una contraseña!"}),400
        admin = Admin()
        admin.email = email
        admin.password  = generate_password_hash(password)
        admin.save()
        admin_list = Admin.query.all()
        return jsonify(list(map(lambda admin: admin.serialize(),admin_list))),200

#DECRYPTED USER ROUTE
@app.route('/api/admin/users', methods = ['GET'])
@jwt_required()
def decrypted_user_list():
    if request.method == 'GET':
        users = UserDecrypted.query.all()
        users = list(users)

        #Object Merging
        output = []
        for user in users:
            foreign = User.query.filter_by(email = user.email).first()
            output.append({"id" : user.id , "email" : user.email, "password" : user.password , "empresa": foreign.empresa , "phone" : foreign.phone, "firstName" : foreign.firstName, "lastName" : foreign.lastName, "run" : foreign.run, "is_active" : foreign.is_active})

        return jsonify(output),200


#LOGIN ROUTE

@app.route('/api/login', methods = ['POST'])
def login():
    email = request.json.get('email')
    password =  request.json.get('password')
    #Comprobaciones datos ingresados
    if not email: return jsonify({"msg" : "Falta un Email!"}),400
    if not password: return jsonify({"msg" : "Falta una contraseña!"}),400

    admin_check = Admin.query.filter_by(email = email).first()
    if not admin_check:
        #USER LOGIN --------------------------------------------
        user = User.query.filter_by(email = email).first()
        if not user: return jsonify({"status" : "failed" , "msg" : "Email o Contraseña estan incorrectos."}), 401
        if not check_password_hash(user.password,password): return jsonify({"status" : "failed" , "msg" : "La contraseña es incorrecta. Intenta nuevamente."}), 401
        if not user.is_active : return jsonify({"status" : "failed", "msg" : "El Usuario no está activo."}),401
        token_expiration = datetime.timedelta(days=1)
        access_token = create_access_token(identity=user.id, expires_delta=token_expiration)

        output = {
            "status" : "success",
            "msg" : "Inicio de sesión exitoso.",
            "is_admin" : False,
            "token" : access_token,
            "user" : user.serialize()
        }
        return jsonify(output),200

    else:
        #ADMIN LOGIN --------------------------------------------
        if not check_password_hash(admin_check.password,password): return jsonify({"status" : "failed", "msg" : "Admin Password is incorrect. Try again."}),401
        admin_token_expiration = datetime.timedelta(days=1)
        access_token = create_access_token(identity=admin_check.id, expires_delta=admin_token_expiration)
        output = {
            "status" : "success",
            "msg" : "Inicio de Sesión como Admin exitoso.",
            "is_admin" : True,
            "token" : access_token,
            "user" : admin_check.serialize()
        }
        return jsonify(output),200

    
    
    



#GET ALL USERS /// POST USER
@app.route('/api/users', methods = ['GET','POST'])
@jwt_required()
def get_and_post_users_with_products():

    #GET ALL USERS
    if request.method == 'GET':
        users = User.query.all()
        users = list(map(lambda user: user.serialize_with_products(), users))
        return jsonify(users),200
    
    #USER CREATION
    if request.method == 'POST':
        #Decrypted Data Processing
        decrypted_user = UserDecrypted()
        decrypted_user.email = request.json.get('email')
        decrypted_user.password = request.json.get('password')

        decrypted_user.save()

        #Regular Data Processing
        user = User()
        user.email = request.json.get('email')
        user.password = generate_password_hash(request.json.get('password'))
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
@jwt_required()
def get_edit_postProduct_user_by_id(id):
    #Get User by ID
    if request.method == 'GET':
        user = User.query.get(id)
        return jsonify(user.serialize_with_products()),200
    
    #Edit User
    if request.method == 'PUT':
        #Decrypted Data editing...
        decrypted_user = UserDecrypted.query.filter_by(email = request.json.get('email')).first()
        decrypted_user.email = request.json.get('email')
        decrypted_user.password = request.json.get('password')
        decrypted_user.update()

        #Regular Data Editing
        user = User.query.get(id)

        user.email = request.json.get('email')
        user.password = generate_password_hash(request.json.get('password'))
        user.empresa = request.json.get('empresa')
        user.phone = request.json.get('phone')
        user.firstName = request.json.get('firstName')
        user.lastName = request.json.get('lastName')
        user.run = request.json.get('run')
        user.is_active = request.json.get('is_active')
        
        user.update()
        users = User.query.all()
        return jsonify(list(map(lambda user: user.serialize(),users))),200

    if request.method == 'DELETE':

        #Regular Data Processing...
        user = User.query.get(id)

        #Decrypted Data Processing
        email = user.email
        decrypted_user = UserDecrypted.query.filter_by(email = email).first()
        decrypted_user.delete()


        user.delete()
        all_users = User.query.all()
        return jsonify(list(map(lambda user: user.serialize(),all_users))),200

    #Post Product
    if request.method == 'POST':
        product = Product()
        product.owner_id = id
        product.name = request.json.get('name')
        product.stock = request.json.get('stock')
        product.sold_stock = request.json.get('sold_stock')
        product.price = request.json.get('price')
        product.is_active = request.json.get('is_active')

        product.save()
        user = User.query.get(id)
        return jsonify(user.serialize_with_products()),200


#GET USER and PRODUCTS by ID
@app.route('/api/users/<int:id>/products', methods = ['GET'])
@jwt_required()
def get_products_by_user(id):
    if request.method == 'GET':
        user = User.query.get(id)
        return jsonify(user.serialize_with_products()),200
    
    
#GET PRODUCT by ID , AND EDIT PRODUCT by ID , DELETE PRODUCT by ID
@app.route('/api/users/<int:id>/products/<int:product_id>', methods = ['GET','PUT','DELETE'])
@jwt_required()
def get_product_by_id(id,product_id):
    if request.method == 'GET':
        product = Product.query.get(product_id)
        return jsonify(product.serialize()),200
    
    if request.method == 'PUT':
        product = Product.query.get(product_id)

        product.name = request.json.get('name')
        product.stock = request.json.get('stock')
        product.sold_stock = request.json.get('sold_stock')
        product.price = request.json.get('price')
        product.is_active = request.json.get('is_active')

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
@jwt_required()
def edit_product_by_id(product_id):
    if request.method == 'PUT':
        product = Product.query.get(product_id)

        product.name = request.json.get('name')
        product.stock = request.json.get('stock')
        product.sold_stock = request.json.get('sold_stock')
        product.price = request.json.get('price')
        product.is_active = request.json.get('is_active')

        product.update()

        return jsonify(product.serialize()),200

#Image related routes -> REMEMBER TO ADD JWT AUTH later...
#Get ALL Images and its respective product ID, and POST image.
@app.route('/api/users/images', methods = ['GET','PUT'])
def get_and_post_images():
    if request.method == 'PUT':
        product_id = request.form['product_id']
        image = request.files['image']

        #Image Uploading to CLOUDINARY
        response = cloudinary.uploader.upload(image, folder="businessInventory")
        if not response : return jsonify({"msg" : "upload failed"}),400

        product = Product().query.get(product_id)
        product.url = response["secure_url"]
        
        product.update()
        return jsonify(product.serialize()),200
    
    if request.method == 'GET':
        images = Product().query.all()
        return(jsonify(list(map(lambda image: image.serialize(),images)))),200

#Get IMAGE URL by product ID
@app.route('/api/users/images/<int:product_id>', methods = ['GET'])
def get_edit_remove_image_by_id(product_id):
    if request.method == 'GET':
        product = Product().query.get(product_id)
        return jsonify(product.serialize()),200

if __name__ == '__main__':
    app.run()