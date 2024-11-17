import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

def send_email_with_sendgrid(to_email, subject, content):
    """Send an email using SendGrid."""
    message = Mail(
        from_email='your_email@example.com',
        to_emails=to_email,
        subject=subject,
        html_content=content
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return response.status_code, response.body
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return None
