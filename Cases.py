from flask import Blueprint, Flask, request, jsonify
from datetime import datetime
from Models import db, advocate_case_association
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enables CORS for all routes by default

# Blueprint for cases
cases_bp = Blueprint('cases', __name__)




# Case model
class Case(db.Model):
    __tablename__ = 'cases'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="open")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    advocates = db.relationship('Advocate', secondary='advocate_case_association', back_populates='cases', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'advocates': [advocate.to_dict() for advocate in self.advocates]
        }

# Add a new case
@cases_bp.route('/', methods=['POST'])
def add_case():
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['title', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        # Create and save the case
        case = Case(
            title=data['title'],
            description=data['description']
        )
        db.session.add(case)
        db.session.commit()

        return jsonify(case.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# View all cases
@cases_bp.route('/', methods=['GET'])
def get_all_cases():
    try:
        cases = Case.query.all()
        return jsonify([case.to_dict() for case in cases]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# View case by ID
@cases_bp.route('/<int:case_id>', methods=['GET'])
def get_case_by_id(case_id):
    try:
        case = Case.query.get(case_id)
        if not case:
            return jsonify({'error': 'Case not found'}), 404

        return jsonify(case.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update a case
@cases_bp.route('/<int:case_id>', methods=['PUT'])
def update_case(case_id):
    try:
        case = Case.query.get(case_id)
        if not case:
            return jsonify({'error': 'Case not found'}), 404

        data = request.get_json()
        case.title = data.get('title', case.title)
        case.description = data.get('description', case.description)
        case.status = data.get('status', case.status)
        case.updated_at = datetime.utcnow()

        db.session.commit()
        return jsonify(case.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Handle CORS preflight requests
@cases_bp.route('/', methods=['OPTIONS'])
def handle_options():
    response = jsonify({'message': 'CORS preflight successful'})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    return response, 200
