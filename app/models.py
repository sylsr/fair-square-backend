from datetime import datetime, timezone
from marshmallow import Schema, fields
import uuid

from app import db

# Database Models
class EmailTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # System-generated template ID
    name = db.Column(db.String(255), nullable=False, unique=True)  # Unique template name
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    versions = db.relationship('EmailTemplateVersion', backref='template', lazy=True)

class EmailTemplateVersion(db.Model):
    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  # Primary UUID
    template_id = db.Column(db.Integer, db.ForeignKey('email_template.id'), nullable=False)
    version = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('template_id', 'version', name='uq_template_version'),
    )

class SentEmail(db.Model):
    uuid = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    template_version_id = db.Column(db.String(36), db.ForeignKey('email_template_version.uuid'), nullable=False)
    recipient = db.Column(db.String(255), nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    opened = db.Column(db.Boolean, default=False)
    clicked = db.Column(db.Boolean, default=False)
    postmark_message_id = db.Column(db.String(255), nullable=True)  # Add this field to store Postmark Message ID


# API Schemas
class EmailTemplateAPISchema(Schema):
    template_id = fields.Int(dump_only=True)  # System-generated template ID
    name = fields.Str(required=True)  # Template name
    created_at = fields.DateTime(dump_only=True)  # Automatically generated timestamp

class EmailTemplateVersionSchema(Schema):
    uuid = fields.Str(dump_only=True)  # UUID is the primary identifier
    template_id = fields.Int(dump_only=True)  # Linked to the EmailTemplate model
    version = fields.Int(dump_only=True)  # Version number for the template
    subject = fields.Str(required=True)  # Subject of the email
    body = fields.Str(required=True)  # Body content of the email
    name = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)  # Automatically generated timestamp

class SentEmailSchema(Schema):
    template_version_id = fields.Str(dump_only=True)  # Marked as dump_only to only appear in the response
    recipient = fields.Str(required=True)  # The recipient is required in the request
    sent_at = fields.DateTime(dump_only=True)  # Automatically generated timestamp
    opened = fields.Boolean(dump_only=True)  # Whether the email was opened
    clicked = fields.Boolean(dump_only=True)  # Whether any links in the email were clicked

