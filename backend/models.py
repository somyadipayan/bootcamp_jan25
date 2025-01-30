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

class Campaign(db.Model):
    __tablename__ = 'campaigns'
    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor_profiles.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text )
    goals = db.Column(db.Integer)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    visibility = db.Column(db.String(10), nullable=False) # public or private
    budget = db.Column(db.Float, nullable=False)
    
    sponsor_profile = db.relationship('SponsorProfile', backref = 'campaigns')
    ad_requests = db.relationship('AdRequests', back_populates = 'campaign', cascade="all, delete-orphan")

class AdRequests(db.Model):
    __tablename__ = 'ad_requests'
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer_profiles.id'), nullable=False) 
    requirements = db.Column(db.Text)
    sent_by = db.Column(db.String(100), nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False) # Pending, Accepted, Declined

    campaign = db.relationship('Campaign', back_populates = 'ad_requests')
    influencer = db.relationship('InfluencerProfile', backref = 'ad_requests')
    
class Negotiations(db.Model):
    __tablename__ = 'negotiations'
    id = db.Column(db.Integer, primary_key=True)
    ad_request_id = db.Column(db.Integer, db.ForeignKey('ad_requests.id'), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    temporary_payment_amount = db.Column(db.Float, nullable=False)
    message = db.Column(db.Text)
    sent_by = db.Column(db.String(100), nullable=False)
    
    ad_request = db.relationship('AdRequests', backref = 'negotiations')