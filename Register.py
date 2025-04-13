from flask import Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re  # For email validation
import logging
from Models import db

# Setup logging
logging.basicConfig(level=logging.ERROR)

# LawFirm model
class LawFirm(db.Model):
    __tablename__ = 'law_firms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Register blueprint
register_bp = Blueprint('register', __name__)

# Route to register a new law firm
@register_bp.route('/register', methods=['OPTIONS', 'POST'])
def register_law_firm():
    if request.method == 'OPTIONS':
        return jsonify({}), 200  # Respond to preflight requests

    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'address']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        # Validate email
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, data['email']):
            return jsonify({'error': 'Invalid email format'}), 400

        # Check if law firm already exists
        existing_firm = LawFirm.query.filter((LawFirm.name == data['name']) | (LawFirm.email == data['email'])).first()
        if existing_firm:
            return jsonify({'error': 'Law firm already exists'}), 409

        # Create new law firm
        new_firm = LawFirm(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            address=data['address']
        )
        db.session.add(new_firm)
        db.session.commit()

        return jsonify(new_firm.to_dict()), 201
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return jsonify({'error': 'An internal server error occurred'}), 500
