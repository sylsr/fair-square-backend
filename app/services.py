from postmarker.core import PostmarkClient
from flask import current_app

from app import db
from app.models import SentEmail


def send_email(recipient, template_version):
    client = PostmarkClient(server_token=current_app.config['POSTMARK_API_TOKEN'])

    # Send the email using Postmark and capture the response
    response = client.emails.send(
        From="tyler@manningmail.com", #hard coded because I have to use email with same domain in my sandbox account
        To=recipient,
        Subject=template_version.subject,
        HtmlBody=template_version.body,
        TextBody=template_version.body,
        MessageStream="outbound"  # Optional: Specify the message stream
    )

    # Log the sent email with the Postmark Message ID
    sent_email = SentEmail(
        template_version_id=template_version.uuid,
        recipient=recipient,
        postmark_message_id=response['MessageID']  # Store the Message ID
    )
    db.session.add(sent_email)
    db.session.commit()


def update_email_engagement():
    client = PostmarkClient(server_token=current_app.config['POSTMARK_API_TOKEN'])

    sent_emails = SentEmail.query.filter_by(opened=False, clicked=False).all()

    for sent_email in sent_emails:
        if not sent_email.postmark_message_id:
            continue
        # Query Postmark for the latest engagement status using the Postmark Message ID
        email_status = client.emails.get(sent_email_id=sent_email.postmark_message_id)

        if email_status.get('Opened'):
            sent_email.opened = True

        if email_status.get('Clicked'):
            sent_email.clicked = True

        db.session.commit()

    print(f"Updated engagement status for {len(sent_emails)} emails.")