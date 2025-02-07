from flask_mail import Mail, Message
from flask import current_app as app

mail = Mail()

def send_email(subject, to, body=None):
    sender = 'noreply@iescp.com'
    with app.app_context():
        msg = Message(subject, recipients=[to], sender=sender, html=body)
        mail.send(msg)
