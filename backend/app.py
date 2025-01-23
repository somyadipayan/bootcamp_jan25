from flask import Flask, request, jsonify
from models import *
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///iescp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'

db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)
CORS(app, supports_credentials=True)

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

if __name__ == '__main__':
    app.run(debug=True)