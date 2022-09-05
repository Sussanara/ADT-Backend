from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

db = SQLAlchemy()

#Admin Table
class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(200), nullable = False , unique = True )
    password = db.Column(db.String(200), nullable = False)
    is_active = db.Column(db.Boolean, default = True)

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "password" : self.password,
            "is_active" : self.is_active
        }

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

#This table only exists to see user info via Admin dashboard.
class UserDecrypted(db.Model):
    __tablename__ = 'userdecrypted'
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(200), nullable = False, unique = True)
    password = db.Column(db.String(200), nullable = False, unique = True)



    def serialize(self):
        return{
            "id": self.id,
            "email": self.email,
            "password": self.password,
        }
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()



class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(200), nullable = False , unique = True)
    password = db.Column(db.String(200) , nullable = False)
    empresa = db.Column(db.String(200), nullable = False , unique = True)
    phone = db.Column(db.String(200), nullable = False)
    firstName = db.Column(db.String(200), nullable = False)
    lastName = db.Column(db.String(200), nullable = False)
    run  = db.Column(db.String(200), nullable = False , unique = True)
    is_active = db.Column(db.Boolean, default = True)
    products = db.relationship('Product', backref='user')

    def serialize(self):
        return{
            "id" : self.id,
            "email" :  self.email,
            "password" : self.password,
            "is_active" : self.is_active,
            "empresa" : self.empresa,
            "phone" : self.phone,
            "firstName" : self.firstName,
            "lastName" : self.lastName,
            "run" : self.run
        }

    def serialize_with_products(self):
        return{
            "id" : self.id,
            "email" : self.email,
            "password" : self.password,
            "is_active": self.is_active,
            "empresa" : self.empresa,
            "phone" : self.phone,
            "firstName" : self.firstName,
            "lastName" : self.lastName,
            "run" : self.run,
            "products": self.get_products()
        }
    
    #Getting products as a list for easy serialization
    def get_products(self):
        return list(map(lambda product: product.serialize(),self.products))

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key = True)
    url = db.Column(db.String(200))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(200), nullable = False)
    stock  = db.Column(db.Integer, nullable = False)
    sold_stock = db.Column(db.Integer, nullable = False)
    price = db.Column(db.Integer, nullable = False)
    is_active = db.Column(db.Boolean, default = True)

    def serialize(self):
        return{
            "id" : self.id,
            "owner_id" : self.owner_id,
            "url" : self.emptify(),
            "name" : self.name,
            "stock" : self.stock,
            "sold_stock" : self.sold_stock,
            "price" : self.price,
            "is_active" : self.is_active
        }

    #This little function sends an empty string instead of NULL
    def emptify(self):
        if not self.url:
            return ""
        else:
            return self.url

    #Database Interaction functions...
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

