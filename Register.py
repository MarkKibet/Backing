from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from Models import db

# Create Blueprint
register_bp = Blueprint('register', __name__)

# Models
class LawFirm(db.Model):
    __tablename__ = 'law_firms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    admin_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

class Advocates(db.Model):
    __tablename__ = 'advocates_login'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    law_firm_id = db.Column(db.Integer, db.ForeignKey('law_firms.id'), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


# Law Firm Registration Route
@register_bp.route('/register', methods=['POST'])
def register_law_firm():
    data = request.json

    # Check if email or name already exists
    if LawFirm.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email already exists"}), 400

    # Create new Law Firm
    law_firm = LawFirm(
        name=data['law_firm_name'],
        admin_name=data['admin_name'],
        email=data['email']
    )
    law_firm.set_password(data['password'])

    db.session.add(law_firm)
    db.session.commit()

    return jsonify({"message": "Law Firm registered successfully!"})


# Advocate Login Route
@register_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    law_firm_name = data['law_firm_name']
    advocate_name = data['advocate_name']
    password = data['password']

    # Validate Law Firm and Advocate
    law_firm = LawFirm.query.filter_by(name=law_firm_name).first()
    if not law_firm:
        return jsonify({"message": "Invalid Law Firm name."}), 401

    advocate = Advocates.query.filter_by(name=advocate_name, law_firm_id=law_firm.id).first()
    if not advocate or not check_password_hash(advocate.password_hash, password):
        return jsonify({"message": "Invalid Advocate credentials."}), 401

    return jsonify({"message": "Login successful!"})

