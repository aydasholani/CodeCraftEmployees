import requests
import json
from flask_sqlalchemy import SQLAlchemy
from flask_security import RoleMixin, UserMixin, SQLAlchemyUserDatastore, hash_password
import datetime  # Added datetime import

NR_OF_PERSON_TO_SEED = 200
SEED = 'Unicorn'

db = SQLAlchemy()

# Define models for users and roles
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    active = db.Column(db.Boolean())
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('user', lazy='dynamic'))

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    age = db.Column(db.String(30))
    street_name = db.Column(db.String(100))
    street_number = db.Column(db.String(20))
    postcode = db.Column(db.String(30))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(30))
    pictures = db.relationship('EmployeePicture', back_populates='employee', lazy=True)
    
    
class EmployeePicture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    picture_size = db.Column(db.String(100))
    picture = db.Column(db.String(100))
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    employee = db.relationship('Employee', back_populates='pictures', lazy=True)

# Set up Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)

def seed_data():
    admin_role = user_datastore.find_or_create_role(name='Admin')
    user_role = user_datastore.find_or_create_role(name='User')
    
    if not User.query.first():
        user_datastore.create_user(email='admin_user@mail.com', password=hash_password('password'), roles=[admin_role, user_role], confirmed_at=datetime.datetime.now())
        user_datastore.create_user(email='user@mail.com', password=hash_password('password'), roles=[user_role], confirmed_at=datetime.datetime.now())
        user_datastore.create_user(email='admin@mail.com', password=hash_password('password'), roles=[admin_role], confirmed_at=datetime.datetime.now())
    
    if Employee.query.count() < NR_OF_PERSON_TO_SEED:
        req = requests.get(f'https://randomuser.me/api/?results={NR_OF_PERSON_TO_SEED}&seed={SEED}')
        if req.status_code != 200:
            raise ValueError('Unable to fetch data! Status code not 200!')

        data = req.json()
        list_of_persons = data['results']

        for employee in list_of_persons:
            new_person = Employee(
                name = employee['name']['first'] + ' ' + employee['name']['last'],
                email = employee['email'],
                phone = employee['phone'],
                age = employee['dob']['age'],
                street_name = employee['location']['street']['name'],
                street_number = employee['location']['street']['number'],
                postcode = employee['location']['postcode'],
                city = employee['location']['city'],
                state = employee['location']['state'],
                country = employee['location']['country']
            )
            
            db.session.add(new_person)
            db.session.commit()
            for key,val in employee['picture'].items():
                p = EmployeePicture(
                        picture_size = key,
                        picture = val,
                        employee_id = new_person.id
                )                
                db.session.add(p)
            db.session.commit()

