from flask import Blueprint, request, jsonify
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from Models import db, advocate_case_association

# Advocate model
class Advocate(db.Model):
    __tablename__ = 'advocates'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with cases
    cases = db.relationship(
        'Case',
        secondary=advocate_case_association,
        back_populates='advocates',
        lazy='dynamic'
    )

    # Password handling methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Convert Advocate object to dictionary
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Blueprint for advocate-related routes
advocates_bp = Blueprint('advocates', __name__)

# Get all advocates
@advocates_bp.route('/', methods=['GET'])
def get_advocates():
    try:
        advocates = Advocate.query.all()
        return jsonify([advocate.to_dict() for advocate in advocates]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Create a new advocate
@advocates_bp.route('/', methods=['POST'])
def create_advocate():
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        # Create and save advocate
        advocate = Advocate(
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        advocate.set_password(data['password'])
        db.session.add(advocate)
        db.session.commit()

        return jsonify(advocate.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Assign advocate to a case
@advocates_bp.route('/assign', methods=['POST'])
def assign_advocate_to_case():
    try:
        data = request.get_json()

        # Validate required fields
        if 'advocate_id' not in data or 'case_id' not in data:
            return jsonify({'error': 'advocate_id and case_id are required'}), 400

        # Fetch advocate and case from the database
        advocate_id = data['advocate_id']
        case_id = data['case_id']
        primary_advocate = data.get('primary_advocate', False)

        advocate = Advocate.query.get(advocate_id)
        if not advocate:
            return jsonify({'error': 'Advocate not found'}), 404

        case = case.query.get(case_id)  # Fixed reference to 'Case' model
        if not case:
            return jsonify({'error': 'Case not found'}), 404

        # Assign advocate to case if not already assigned
        if advocate not in case.advocates:
            case.advocates.append(advocate)
            db.session.commit()

        # Update additional fields in the association table
        db.session.execute(
            advocate_case_association.update()
            .where(
                (advocate_case_association.c.advocate_id == advocate_id) & 
                (advocate_case_association.c.case_id == case_id)
            )
            .values(
                primary_advocate=primary_advocate,
                assigned_date=datetime.utcnow()
            )
        )
        db.session.commit()

        return jsonify({'message': 'Advocate assigned to case successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
