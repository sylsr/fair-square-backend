from flask import Blueprint, request, jsonify
from flask_apispec import doc, marshal_with, use_kwargs
from app.models import EmailTemplate, EmailTemplateAPISchema, EmailTemplateVersion, EmailTemplateVersionSchema
from app import db

bp = Blueprint('api', __name__)

@bp.route('/templates', methods=['POST'])
@doc(
    description='Create a new email template',
    tags=['Email Templates'],
)
@use_kwargs(EmailTemplateAPISchema, location='json')  # This replaces the body argument
@marshal_with(EmailTemplateAPISchema, code=201)
def create_template(**kwargs):
    schema = EmailTemplateAPISchema()
    try:
        validated_data = schema.load(kwargs)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    template = EmailTemplate(**validated_data)
    db.session.add(template)
    db.session.commit()

    return template, 201


@bp.route('/templates/<int:template_id>/versions', methods=['POST'])
@doc(
    description='Create a new version of an email template',
    tags=['Email Templates'],
)
@use_kwargs(EmailTemplateVersionSchema, location='json')
@marshal_with(EmailTemplateVersionSchema, code=201)
def create_template_version(template_id, **kwargs):
    schema = EmailTemplateVersionSchema()
    try:
        # Validate and load the data
        validated_data = schema.load(kwargs)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # Get the original template by template_id
    template = EmailTemplate.query.get_or_404(template_id)

    # Create the new version based on validated data
    version_number = len(template.versions) + 1
    version = EmailTemplateVersion(
        template_id=template.id,
        version=version_number,
        subject=validated_data['subject'],
        body=validated_data['body']
    )

    # Save the new version to the database
    db.session.add(version)
    db.session.commit()

    return jsonify({'id': version.id}), 201