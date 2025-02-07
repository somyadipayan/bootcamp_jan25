from flask import Flask, request, jsonify, send_file, Response
from models import *
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies
from datetime import datetime
import workers, task
from mailer import mail
from io import BytesIO, StringIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask_caching import Cache

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///iescp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['MAIL_SERVER'] = 'localhost'
app.config['MAIL_PORT'] = 1025
app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'

db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)
CORS(app, supports_credentials=True)
mail.init_app(app)
cache = Cache(app)
celery = workers.celery

celery.conf.update(
    broker_url='redis://localhost:6379/1',
    result_backend='redis://localhost:6379/2'
)

celery.Task = workers.ContextTask
app.app_context().push()

def create_admin():
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@iescp.com',
            password='1',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()

with app.app_context(): 
    db.create_all()
    create_admin()

@app.route('/')
def hello_world():
    task.add.delay(1,4)
    return 'Hello, World!'

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Common data for all users
    role = data['role']
    
    if role not in ['sponsor', 'influencer']:
        return jsonify({"error":'Invalid role'}), 400

    username = data['username']
    email = data['email']
    password = data['password']


    if not username or not email or not password or not role:
        return jsonify({"error":'Please fill in all the required fields'}), 400

    existing_user = User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error":'User already exists'}), 400

    new_user = User(username=username, email=email, password=password, role=role)
    
    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        return jsonify({"error":f'Something went wrong: {str(e)}'}), 500
        
    # Role-specific data
    # Sponsor
    if role == 'sponsor':
        company_name = data['company_name']
        industry = data['industry']
        budget = data['budget']

        print(company_name, industry, budget)

        if not company_name or not industry or not budget:
            return jsonify({"error":'Please fill in all the required fields'}), 400

        if budget < 0:
            return jsonify({"error":'Budget cannot be negative'}), 400
    
        sponsor_profile = SponsorProfile(
            user_id=new_user.id,
            company_name=company_name,
            industry=industry,
            budget=budget
            )
        
        try:
            db.session.add(sponsor_profile)
            db.session.commit()
        except Exception as e:
            return jsonify({"error":f'Something went wrong: {str(e)}'}), 500

    # Influencer
    elif role == 'influencer':
        name = data['name']
        category = data['category']
        niche = data['niche']
        reach = data['reach']

        if not name or not category or not niche or not reach:
            return jsonify({"error":'Please fill in all the required fields'}), 400

        if reach < 0:
            return jsonify({"error":'Reach cannot be negative'}), 400
        
        influencer_profile = InfluencerProfile(
            user_id=new_user.id,
            name=name,
            category=category,
            niche=niche,
            reach=reach
            )
        try:
            db.session.add(influencer_profile)
            db.session.commit()
        except Exception as e:
            return jsonify({"error":f'Something went wrong: {str(e)}'}), 500    

    return jsonify({"message":'User registered successfully'}), 200


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    if not username or not password:
        return jsonify({"error": "Please fill in all the required fields"}), 400
    user = User.query.filter_by(username=username).first()
    # if the user is found and password is correct
    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity={'id': user.id,
                                                    'role': user.role,
                                                    'username': user.username})
        return jsonify({"message": "Login successful", "access_token":access_token}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    print(current_user)
    return jsonify({"message": "This is a protected route"}), 200

@app.route('/admin', methods=['GET'])
@jwt_required()
def admin():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"error": "You must be an admin to access this route"}), 401
    return jsonify({"message": "This is an admin route"}), 200

@app.route("/getuserinfo", methods=["GET"])
@jwt_required()
def get_user_info():
    current_user = get_jwt_identity()
    return jsonify(current_user), 200

@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)
    return response, 200

# CRUD on Campaigns
# CREATE
@app.route('/campaign', methods=['POST'])
@jwt_required()
def create_campaign():
    current_user = get_jwt_identity()
    if current_user['role'] != 'sponsor':
        return jsonify({"error": "You must be a sponsor to create campaigns"}), 401
    
    sponsor = SponsorProfile.query.filter_by(user_id=current_user['id']).first()

    data = request.get_json()
    sponsor_id = sponsor.id
    name = data['name']
    description = data['description']
    goals = data['goals']
    start_date = data['start_date']
    end_date = data['end_date']
    visibility = data['visibility']
    budget = data['budget']
    
    if not name or not visibility or not budget:
        return jsonify({"error":'Please fill in all the required fields'}), 400
    
    if budget < 0:
        return jsonify({"error":'Budget cannot be negative'}), 400

    new_campaign = Campaign(sponsor_id=sponsor_id,
                            name=name,
                            description=description,
                            goals=goals,
                            start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
                            end_date=datetime.strptime(end_date, '%Y-%m-%d').date(),
                            visibility=visibility,
                            budget=budget)
    
    try:
        db.session.add(new_campaign)
        db.session.commit()
    except Exception as e:
        return jsonify({"error":f'Something went wrong: {str(e)}'}), 500

    return jsonify({"message":'Campaign created successfully'}), 200

# UPDATE # SPONSOR who created the campaign
@app.route('/campaign/<int:campaign_id>', methods=['PUT'])
@jwt_required()
def update_campaign(campaign_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'sponsor':
        return jsonify({"error": "You must be a sponsor to update campaigns"}), 401
    
    sponsor = SponsorProfile.query.filter_by(user_id=current_user['id']).first()

    campaign = Campaign.query.filter_by(id=campaign_id).first()

    if not campaign:
        return jsonify({"error": "Campaign not found"}), 404
    
    if campaign.sponsor_id != sponsor.id:
        return jsonify({"error": "You do not have permission to update this campaign"}), 403

    data = request.get_json()
    
    if not data['name'] or not data['visibility'] or not data['budget']:
        return jsonify({"error":'Please fill in all the required fields'}), 400

    campaign.name = data['name']
    campaign.description = data['description']
    campaign.goals = data['goals']
    campaign.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    campaign.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    campaign.visibility = data['visibility']
    campaign.budget = data['budget']
    try:
        db.session.commit()
    except Exception as e:
        return jsonify({"error":f'Something went wrong: {str(e)}'}), 500

    return jsonify({"message":'Campaign updated successfully'}), 200

# READ A SPECIFIC CAMPAIGN BY ID
@app.route('/campaign/<int:campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id).first()
    if not campaign:
        return jsonify({"error": "Campaign not found"}), 404

    campaign_data = {
        "id": campaign.id,
        "sponsor_id": campaign.sponsor_id,
        "sponsor": campaign.sponsor_profile.company_name,
        "name": campaign.name,
        "description": campaign.description,
        "goals": campaign.goals,
        "start_date": datetime.strftime(campaign.start_date, '%Y-%m-%d'), # Convert datetime to string in 'YYYY-MM-DD' format
        "end_date":datetime.strftime(campaign.end_date, '%Y-%m-%d'),
        "visibility": campaign.visibility,
        "budget": campaign.budget
    }
    return jsonify(campaign_data), 200

# READ ALL CAMPAIGNS
@app.route('/public_campaigns', methods=['GET'])
def get_public_campaigns():
    campaigns = Campaign.query.filter_by(visibility='public').all()

    campaign_data = []
    for campaign in campaigns:
        campaign_data.append({
            "id": campaign.id,
            "sponsor_id": campaign.sponsor_id,
            "sponsor": campaign.sponsor_profile.company_name,
            "name": campaign.name,
            "description": campaign.description,
            "goals": campaign.goals,
            "start_date": datetime.strftime(campaign.start_date, '%Y-%m-%d'), # Convert datetime to string in 'YYYY-MM-DD' format
            "end_date":datetime.strftime(campaign.end_date, '%Y-%m-%d'),
            "visibility": campaign.visibility,
            "budget": campaign.budget
        })

    return jsonify(campaign_data), 200

@app.route('/my-campaigns', methods=['GET'])
@jwt_required()
def get_my_campaigns():
    current_user = get_jwt_identity()
    if current_user['role'] != 'sponsor':
        return jsonify({"error": "You must be a sponsor to view your campaigns"}), 401

    sponsor = SponsorProfile.query.filter_by(user_id=current_user['id']).first()
    campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()

    campaign_data = []
    for campaign in campaigns:
        campaign_data.append({
            "id": campaign.id,
            "sponsor_id": campaign.sponsor_id,
            "sponsor": campaign.sponsor_profile.company_name,
            "name": campaign.name,
            "description": campaign.description,
            "goals": campaign.goals,
            "start_date": datetime.strftime(campaign.start_date, '%Y-%m-%d'), # Convert datetime to string in 'YYYY-MM-DD' format
            "end_date":datetime.strftime(campaign.end_date, '%Y-%m-%d'),
            "visibility": campaign.visibility,
            "budget": campaign.budget
        })

    return jsonify(campaign_data), 200

@app.route('/all_influencers', methods=['GET'])
def get_all_influencers():
    influencers = InfluencerProfile.query.all()
    if not influencers:
        return jsonify({"error": "No influencers found"}), 404

    influencers_data = []
    for influencer in influencers:
        # Get ads for the influencer which are accepted
        influencer_Ads = AdRequests.query.filter_by(influencer_id=influencer.id).filter_by(status='accepted').all()
        previous_collaborations = []
        for ad in influencer_Ads:
            previous_collaborations.append(ad.campaign.sponsor_profile.company_name)
        influencers_data.append({
            "id": influencer.id,
            "name": influencer.name,
            "category": influencer.category,
            "niche": influencer.niche,
            "reach": influencer.reach,
            "previous_collaborations": previous_collaborations
        })

    return jsonify(influencers_data), 200

@app.route('/campaign/<int:campaign_id>', methods=['DELETE'])
@jwt_required()
def delete_campaign(campaign_id):
    current_user = get_jwt_identity()
    if not (current_user['role'] == 'sponsor' or current_user['role'] == 'admin'):
        return jsonify({"error": "You must be a sponsor or admin to delete campaigns"}), 401
    
    campaign = Campaign.query.filter_by(id=campaign_id).first()

    if not campaign:
        return jsonify({"error": "Campaign not found"}), 404

    if current_user['role'] == 'sponsor':    
        sponsor = SponsorProfile.query.filter_by(user_id=current_user['id']).first()
        if campaign.sponsor_id != sponsor.id:
            return jsonify({"error": "You do not have permission to delete this campaign"}), 403

    try:
        db.session.delete(campaign)
        db.session.commit()
    except Exception as e:
        return jsonify({"error":f'Something went wrong: {str(e)}'}), 500

    return jsonify({"message":'Campaign deleted successfully'}), 200

# Sponsor sends request to influencer (private campaigns)
@app.route('/sponsor/send-ad-request', methods=['POST'])
@jwt_required()
def send_ad_request():
    current_user = get_jwt_identity()
    if current_user['role'] != 'sponsor':
        return jsonify({"error": "You must be a sponsor to send ad requests"}), 401

    sponsor = SponsorProfile.query.filter_by(user_id=current_user['id']).first()

    data = request.get_json()
    campaign = Campaign.query.get_or_404(data['campaignId'])
    
    if campaign.sponsor_id != sponsor.id:
        return jsonify({"error": "You do not have permission to send ad requests for this campaign"}), 403

    ad_request = AdRequests(
        campaign_id = campaign.id,
        influencer_id = data['influencerId'],
        requirements = data['requirements'],
        sent_by = 'sponsor',
        payment_amount = data['paymentAmount'],
        status = 'Pending'
    )
    db.session.add(ad_request)
    db.session.commit()
    return jsonify({"message":'Ad request sent successfully'}), 200

# Influencer sees all the ad requests for him
@app.route('/influencer/ad-requests', methods=['GET'])
@jwt_required()
def get_influencer_ad_requests():
    current_user = get_jwt_identity()
    if current_user['role'] != 'influencer':
        return jsonify({"error": "You must be an influencer to see ad requests"}), 401

    influencer = InfluencerProfile.query.filter_by(user_id=current_user['id']).first()

    ad_requests = AdRequests.query.filter_by(influencer_id=influencer.id).all()
    ad_requests_data = []
    for ad_request in ad_requests:
        ad_requests_data.append({
            "id": ad_request.id,
            "campaign_id": ad_request.campaign_id,
            "sponsor_id": ad_request.campaign.sponsor_id,
            "sponsor": ad_request.campaign.sponsor_profile.company_name,
            "name": ad_request.campaign.name,
            "requirements": ad_request.requirements,
            "sent_by": ad_request.sent_by,
            "payment_amount": ad_request.payment_amount,
            "status": ad_request.status
        })

    return jsonify(ad_requests_data), 200

# Influencer send ad request to sponsor
@app.route('/influencer/send_ad_request', methods=['POST'])
@jwt_required()
def send_influencer_ad_request():
    current_user = get_jwt_identity()
    if current_user['role'] != 'influencer':
        return jsonify({"error": "You must be an influencer to send ad requests"}), 401

    influencer = InfluencerProfile.query.filter_by(user_id=current_user['id']).first()

    data = request.get_json()
    campaign = Campaign.query.get_or_404(data['campaign_id'])

    ad_request = AdRequests(
        campaign_id = campaign.id,
        influencer_id = influencer.id,
        requirements = data['requirements'],
        sent_by = 'influencer',
        payment_amount = data['paymentAmount'],
        status = 'Pending'
    )
    db.session.add(ad_request)
    db.session.commit()
    return jsonify({"message":'Ad request sent successfully'}), 200

# all the ad requests for him
@app.route('/sponsor/ad-requests', methods=['GET'])
@jwt_required()
def get_sponsor_ad_requests():
    current_user = get_jwt_identity()
    if current_user['role'] != 'sponsor':
        return jsonify({"error": "You must be a sponsor to see ad requests"}), 401

    sponsor = SponsorProfile.query.filter_by(user_id=current_user['id']).first()

    ad_requests = AdRequests.query.join(Campaign).filter(Campaign.sponsor_id == sponsor.id).all()
    ad_requests_data = []
    for ad_request in ad_requests:
        ad_requests_data.append({
            "id": ad_request.id,
            "campaign_id": ad_request.campaign_id,
            "name": ad_request.campaign.name,
            "requirements": ad_request.requirements,
            "sent_by": ad_request.sent_by,
            "payment_amount": ad_request.payment_amount,
            "status": ad_request.status,
            "influencer_id": ad_request.influencer_id,
            "influencer": ad_request.influencer.name
        })

    return jsonify(ad_requests_data), 200

@app.route('/accept_ad_request', methods=['PUT'])
@jwt_required()
def accept_ad_request():
    current_user = get_jwt_identity()
    if current_user['role'] not in ['sponsor', 'influencer']:
        return jsonify({"error": "You must be a sponsor or influencer to accept ad requests"}), 401

    data = request.get_json()
    ad_request = AdRequests.query.get_or_404(data['ad_request_id'])

    ad_request.status = 'Accepted'
    ad_request.campaign.budget -= ad_request.payment_amount

    db.session.commit()
    return jsonify({"message":'Ad request accepted successfully'}), 200

@app.route('/reject_ad_request', methods=['PUT'])
@jwt_required()
def reject_ad_request():
    current_user = get_jwt_identity()
    if current_user['role'] not in ['sponsor', 'influencer']:
        return jsonify({"error": "You must be a sponsor or influencer to accept ad requests"}), 401

    data = request.get_json()
    ad_request = AdRequests.query.get_or_404(data['ad_request_id'])

    db.session.delete(ad_request)
    db.session.commit()
    return jsonify({"message":'Ad request rejected successfully'}), 200

# Get Negotiation Details for a specific ad request
@app.route('/negotiation/<int:ad_request_id>', methods=['GET'])
@jwt_required()
def get_negotiation_details(ad_request_id):
    current_user = get_jwt_identity()
    print(current_user)
    if current_user['role'] not in ['sponsor', 'influencer']:
        return jsonify({"error": "You must be a sponsor or influencer to see negotiation details"}), 401

    negotiations = Negotiations.query.filter_by(ad_request_id=ad_request_id).all()
    ad_request = AdRequests.query.get_or_404(ad_request_id)

    messages = []
    for negotiation in negotiations:
        messages.append({
            "time": negotiation.time,
            "message": negotiation.message,
            "sent_by": negotiation.sent_by,
            "temporary_payment_amount": negotiation.temporary_payment_amount
        })


    return jsonify({
        "messages": messages,
        "adRequest": {
            "id": ad_request.id,
            "campaign_id": ad_request.campaign_id,
            "name": ad_request.campaign.name,
            "visibility": ad_request.campaign.visibility,
            "original_payment_amount": ad_request.payment_amount,
            "status": ad_request.status,
            "influencer_id": ad_request.influencer_id,
            "influencer": ad_request.influencer.name,
            "sponsor_id": ad_request.campaign.sponsor_id,
            "sponsor": ad_request.campaign.sponsor_profile.company_name,
            "paymentAmount": ad_request.payment_amount
        },
       
    }), 200

@app.route('/negotiation', methods=['POST'])
@jwt_required()
def add_negotiation():
    current_user = get_jwt_identity()
    print(current_user)
    if current_user['role'] not in ['sponsor', 'influencer']:
        return jsonify({"error": "You must be a sponsor or influencer to add a negotiation"}), 401

    data = request.get_json()
    print(data)
    negotiation = Negotiations(
        ad_request_id = data['ad_request_id'],
        time = datetime.now(),
        temporary_payment_amount = data['temporary_payment_amount'],
        message = data['message'],
        sent_by = current_user['role']
    )
    db.session.add(negotiation)
    db.session.commit()
    return jsonify({"message":'Negotiation added successfully'}), 200

@app.route("/adrequest/finalize", methods=['POST'])
@jwt_required()
def finalize_ad_request():
    current_user = get_jwt_identity()
    if current_user['role'] not in ['sponsor', 'influencer']:
        return jsonify({"error": "You must be a sponsor or influencer to finalize ad requests"}), 401
    data = request.get_json()
    ad_request = AdRequests.query.get_or_404(data['ad_request_id'])

    # GET THE LATEST NEGOTIATION FROM THE AD REQUEST
    if current_user['role'] == 'sponsor':
        negotiations = Negotiations.query.filter_by(ad_request_id=ad_request.id).filter_by(sent_by='influencer').order_by(Negotiations.time.desc()).first()
    else:
        negotiations = Negotiations.query.filter_by(ad_request_id=ad_request.id).filter_by(sent_by='sponsor').order_by(Negotiations.time.desc()).first()

    if not negotiations:
        return jsonify({"error": "No negotiations found for this ad request"}), 404
   
    ad_request.payment_amount = negotiations.temporary_payment_amount
    ad_request.status = 'Accepted'
    db.session.commit()
    return jsonify({"message":'Ad request Accepteds successfully'}), 200



@app.route('/admin/statistics', methods=['GET'])
@cache.cached(timeout=180)
# @jwt_required()
def get_statistics():
    """ Returns a JSON of counts of sponsor, influencers and campaigns for admin """
    # current_user = get_jwt_identity()
    # if current_user['role'] != 'admin':
    #     return jsonify({"error": "You must be an admin to view statistics"}), 401

    total_users = User.query.count()
    total_sponsors = SponsorProfile.query.count()
    total_influencers = InfluencerProfile.query.count()
    total_campaigns = Campaign.query.count()
    total_ad_requests = AdRequests.query.count()

    stats = {
        "total_users": total_users,
        "total_sponsors": total_sponsors,
        "total_influencers": total_influencers,
        "total_campaigns": total_campaigns,
        "total_ad_requests": total_ad_requests
    }

    return jsonify(stats), 200

@cache.cached(timeout=60)
@app.route('/admin/statistics/graph', methods=['GET'])
@jwt_required()
def get_statistics_graph():
    """ Returns a pie chart of count of sponsor and influencers for admin """
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"error": "You must be an admin to view statistics"}), 401

    try:
        labels = ['Sponsors', 'Influencers']
        count = [SponsorProfile.query.count(), InfluencerProfile.query.count()]
        
        fig, ax = plt.subplots()
        ax.pie(count, labels=labels, autopct='%1.1f%%')
        ax.axis('equal')

        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()

        return send_file(img, mimetype='image/png')
    except Exception as e:
        return jsonify({"error": f"Failed to generate graph: {str(e)}"}), 500

import csv
@app.route('/sponsor/csv', methods=['GET'])
@jwt_required()
def get_sponsor_csv():
    """
    Returns a CSV file containing all campaign details for a sponsor
    """
    current_user = get_jwt_identity()
    if current_user['role'] != 'sponsor':
        return jsonify({"error": "You must be a sponsor to view campaign details"}), 401

    sponsor = SponsorProfile.query.filter_by(user_id=current_user['id']).first()
    campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()

    csv_buffer = StringIO()
    csv_writer = csv.writer(csv_buffer)
    csv_writer.writerow(['Campaign ID', 'Name', 'Description', 'Goals', 'Start Date', 'End Date', 'Visibility', 'Budget'])

    for campaign in campaigns:
        csv_writer.writerow([campaign.id, campaign.name, campaign.description, campaign.goals, campaign.start_date, campaign.end_date, campaign.visibility, campaign.budget])

    response = Response(csv_buffer.getvalue(), content_type='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename="sponsor-campaigns.csv"'

    return response

# Clear Cache
@app.route('/clear-cache', methods=['POST'])
def clear_cache():
    cache.clear()
    return jsonify({"message": "Cache cleared successfully"}), 200

# flag a campaign as spam
# @app.route('/campaign/<int:campaign_id>/spam', methods=['POST'])
# @jwt_required()
# def flag_campaign_as_spam(campaign_id):
#     current_user = get_jwt_identity()
#     if current_user['role'] != 'admin':
#         return jsonify({"error": "You must be an admin to flag campaigns as spam"}), 401

#     campaign = Campaign.query.filter_by(id=campaign_id).first()
#     if not campaign:
#         return jsonify({"error": "Campaign not found"}), 404

#     campaign.flag = True
#     db.session.commit()
#     return jsonify({"message":'Campaign marked as spam successfully'}), 200

# flag users as spam
# @app.route('/user/<int:user_id>/spam', methods=['POST'])
# @jwt_required()
# def flag_user_as_spam(user_id):
#     current_user = get_jwt_identity()
#     if current_user['role'] != 'admin':
#         return jsonify({"error": "You must be an admin to flag users as spam"}), 401

#     user = User.query.filter_by(id=user_id).first()
#     if not user:
#         return jsonify({"error": "User not found"}), 404

#     user.flag = True
#     db.session.commit()
#     return jsonify({"message":'User marked as spam successfully'}), 200

# get active users (NOT FLAGGED AS SPAM)
# @app.route('/users', methods=['GET'])
# @jwt_required()
# def get_active_users():
#     current_user = get_jwt_identity()
#     if current_user['role'] != 'admin':
#         return jsonify({"error": "You must be an admin to view active users"}), 401
#     users = User.query.filter_by(flag=False).all()
#     users_data = []

#     for user in users:
#         user_data = {
#             'id': user.id,
#             'username': user.username,
#             'email': user.email,
#             'role': user.role
#         }
#         users_data.append(user_data)

#     return jsonify({"users": users_data}), 200

if __name__ == '__main__':
    app.run(debug=True)