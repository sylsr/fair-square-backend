from datetime import datetime, timezone
from marshmallow import Schema, fields

from app import db

# Database Models
class EmailTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class EmailTemplateVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('email_template.id'), nullable=False)
    version = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class SentEmail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    template_version_id = db.Column(db.Integer, db.ForeignKey('email_template_version.id'), nullable=False)
    recipient = db.Column(db.String(255), nullable=False)
    sent_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    opened = db.Column(db.Boolean, default=False)
    clicked = db.Column(db.Boolean, default=False)

# API Schemas
class EmailTemplateAPISchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    subject = fields.Str(required=True)
    body = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)

class EmailTemplateVersionSchema(Schema):
    id = fields.Int(dump_only=True)
    template_id = fields.Int(required=True)
    version = fields.Int(required=True)
    subject = fields.Str(required=True)
    body = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)

class SentEmailSchema(Schema):
    id = fields.Int(dump_only=True)
    template_version_id = fields.Int(required=True)
    recipient = fields.Str(required=True)
    sent_at = fields.DateTime(dump_only=True)
    opened = fields.Boolean(dump_only=True)
    clicked = fields.Boolean(dump_only=True)
