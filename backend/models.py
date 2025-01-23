from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True ,nullable=False)
    email = db.Column(db.String(120), unique=True ,nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), nullable=False) # sponsor or influencer or admin

    def __init__(self, username, email, password, role):
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.role = role
    
    def __repr__(self):
        return f'User {self.username}'
    
class SponsorProfile(db.Model):
    __tablename__ = 'sponsor_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)    
    industry = db.Column(db.String(100), nullable=False)
    budget = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', backref = 'sponsor_profile')
    def __init__(self, user_id, company_name, industry, budget):
        self.user_id = user_id        
        self.company_name = company_name
        self.industry = industry
        self.budget = budget

class InfluencerProfile(db.Model):
    __tablename__ = 'influencer_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    niche = db.Column(db.String(100), nullable=False)
    reach = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', backref = 'influencer_profile')

    def __init__(self, user_id, name, category, niche, reach):
        self.user_id = user_id
        self.name = name
        self.category = category        
        self.niche = niche
        self.reach = reach