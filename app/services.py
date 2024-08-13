import postmark
from flask import current_app

def send_email(recipient, template_version):
    client = postmark.PMMail(api_key=current_app.config['POSTMARK_API_TOKEN'],
                             sender="your-email@example.com",
                             to=recipient,
                             subject=template_version.subject,
                             text_body=template_version.body,
                             html_body=template_version.body)
    client.send()
