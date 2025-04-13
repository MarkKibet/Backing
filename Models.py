from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()

advocate_case_association = db.Table(
    'advocate_case_association',
    db.Column('advocate_id', db.Integer, db.ForeignKey('advocates.id', ondelete="CASCADE", name="fk_advocate_case_association_advocate"), primary_key=True),
    db.Column('case_id', db.Integer, db.ForeignKey('cases.id', ondelete="CASCADE", name="fk_advocate_case_association_case"), primary_key=True),
    db.Column('assigned_date', db.DateTime, default=datetime.utcnow),
    db.Column('primary_advocate', db.Boolean, default=False),
    extend_existing=True  # Allow redefinition of the table
)
