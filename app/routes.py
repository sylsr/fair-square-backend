import json

from flask import Blueprint, request
from flask_apispec import doc, marshal_with, use_kwargs
from app.models import EmailTemplate, EmailTemplateVersion, EmailTemplateVersionSchema, SentEmail, SentEmailSchema
from app import db
from app.services import send_email as send_email_service, update_email_engagement

bp = Blueprint('api', __name__)

@bp.route('/templates', methods=['POST'])
@doc(
    description='Create a new email template with the initial version',
    tags=['Email Templates']
)
@use_kwargs(EmailTemplateVersionSchema, location='json')
@marshal_with(EmailTemplateVersionSchema, code=201)
def create_template(**kwargs):
    name = kwargs.get('name')
    subject = kwargs.get('subject')
    body = kwargs.get('body')

    existing_template = EmailTemplate.query.filter_by(name=name).first()
    if existing_template:
        return json.dumps({"error": f"Template with name '{name}' already exists"}), 400

    # Create the new template
    template = EmailTemplate(name=name)
    db.session.add(template)
    db.session.commit()

    # Create the initial version for the template
    template_version = EmailTemplateVersion(
        template_id=template.id,
        version=1,  # Initial version
        subject=subject,
        body=body
    )
    db.session.add(template_version)
    db.session.commit()

    return template_version, 201


@bp.route('/templates/<int:template_id>/versions', methods=['POST'])
@doc(
    description='Create a new version of an existing email template',
    tags=['Email Templates']
)
@use_kwargs(EmailTemplateVersionSchema, location='json')
@marshal_with(EmailTemplateVersionSchema, code=201)
def create_template_version(template_id, **kwargs):
    template = EmailTemplate.query.get_or_404(template_id)

    # Determine the next version number
    next_version = len(template.versions) + 1

    # Create the new version for the template
    template_version = EmailTemplateVersion(
        template_id=template.id,
        version=next_version,
        subject=kwargs.get('subject'),
        body=kwargs.get('body')
    )
    db.session.add(template_version)
    db.session.commit()

    return template_version, 201



@bp.route('/templates', methods=['GET'])
@doc(
    description='Retrieve an email template version by UUID or by template name and version',
    params={
        'uuid': {
            'description': 'The globally unique identifier of the email template version',
            'in': 'query',
            'type': 'string',
            'required': False
        },
        'template id': {
            'description': 'The ID of the template',
            'in': 'query',
            'type': 'integer',
            'required': False
        },
        'version': {
            'description': 'The version number of the email template',
            'in': 'query',
            'type': 'integer',
            'required': False
        }
    },
    tags=['Email Templates']
)
@marshal_with(EmailTemplateVersionSchema)
def get_template():
    uuid = request.args.get('uuid')
    template_id = request.args.get('template_id')
    version = request.args.get('version')

    if uuid:
        # Lookup by UUID
        template_version = EmailTemplateVersion.query.filter_by(uuid=uuid).first()
        if not template_version:
            return json.dumps({"error": "Template not found"}), 404

        return template_version, 200

    elif template_id and version:
        template_version = EmailTemplateVersion.query.filter_by(template_id=template_id, version=int(version)).first()
        if not template_version:
            return json.dumps({"error": "Template version not found"}), 404

        return template_version, 200

    else:
        return json.dumps({"error": "Either 'uuid' or both 'name' and 'version' query parameters are required"}), 400


@bp.route('/templates/versions', methods=['GET'])
@doc(
    description='Retrieve all versions of a template by template name',
    params={
        'template_id': {
            'description': 'The id of the email template to get all versions of',
            'in': 'query',
            'type': 'string',
            'required': True
        }
    },
    tags=['Email Templates']
)
@marshal_with(EmailTemplateVersionSchema(many=True))
def get_all_template_versions():
    id = request.args.get('template_id')

    if not id:
        return json.dumps({"error": "'name' query parameter is required"}), 400

    template = EmailTemplate.query.filter_by(id=id).first()
    if not template:
        return json.dumps({"error": "Template not found"}), 404

    versions = EmailTemplateVersion.query.filter_by(template_id=template.id).all()
    return versions, 200

@bp.route('/send-email', methods=['POST'])
@doc(
    description='Send an email based on template UUID',
    params={
        'uuid': {
            'description': 'The UUID of the email template version',
            'in': 'query',
            'type': 'string',
            'required': True
        }
    },
    tags=['Email Sending']
)
@use_kwargs(SentEmailSchema, location='json')
@marshal_with(SentEmailSchema, code=201)
def send_email(**kwargs):
    uuid = request.args.get('uuid')
    recipient = kwargs.get('recipient')

    if not uuid:
        return json.dumps({"error": "'uuid' query parameter is required"}), 400

    # Lookup by UUID
    template_version = EmailTemplateVersion.query.filter_by(uuid=uuid).first()
    if not template_version:
        return json.dumps({"error": "Template version not found"}), 404

    # Use the Postmark API to send the email
    send_email_service(recipient, template_version)

    # Log the sent email
    sent_email = SentEmail(
        template_version_id=template_version.uuid,
        recipient=recipient
    )
    db.session.add(sent_email)
    db.session.commit()

    return sent_email, 201

@bp.route('/analytics/template-version', methods=['GET'])
@doc(
    description='Get the total sends, opens, and clicks for a specific template version by UUID',
    params={
        'uuid': {
            'description': 'The UUID of the email template version',
            'in': 'query',
            'type': 'string',
            'required': True
        }
    },
    tags=['Analytics']
)
def get_template_version_analytics():
    update_email_engagement() #This is really bad, normally we would do this in a cron job. But because this is a simple small demo app I'll do this for now - just know if production I'd put this as a background task.
    uuid = request.args.get('uuid')

    if not uuid:
        return json.dumps({"error": "'uuid' query parameter is required"}), 400

    template_version = EmailTemplateVersion.query.filter_by(uuid=uuid).first()
    if not template_version:
        return json.dumps({"error": "Template version not found"}), 404

    # Query the SentEmail table to get the analytics data
    total_sends = SentEmail.query.filter_by(template_version_id=uuid).count()
    total_opens = SentEmail.query.filter_by(template_version_id=uuid, opened=True).count()
    total_clicks = SentEmail.query.filter_by(template_version_id=uuid, clicked=True).count()

    return json.dumps({
        "uuid": uuid,
        "total_sends": total_sends,
        "total_opens": total_opens,
        "total_clicks": total_clicks
    }), 200


