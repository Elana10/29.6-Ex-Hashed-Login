from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    """ Connect to database."""
    db.app = app
    db.init_app(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    username = db.Column(db.String(20), unique = True, nullable =False, )
    password = db.Column(db.Text, nullable = False)
    email = db.Column(db.String(50), nullable = False, unique = True)
    first_name = db.Column(db.String(30), nullable = False)
    last_name = db.Column(db.String(30), nullable = False)
    feedbacks = db.relationship('Feedback', 
                          backref ='user',
                          cascade='all,delete')
    

    @classmethod
    def register(cls,username,pwd,email,first_name,last_name):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        #return instance of user w/ all info: username, pwd, email, first and last names
        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name,last_name=last_name)
    
    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.
        Returns user if valid; else return False
        """
        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            #return user instance
            return u
        else: 
            return False 

class Feedback(db.Model):
    __tablename__='feedbacks'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    title = db.Column(db.String(100), nullable = False)
    content = db.Column(db.Text, nullable = False)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'), nullable=False)
    # user = db.relationship("User")
    