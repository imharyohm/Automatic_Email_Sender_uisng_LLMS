from celery import shared_task
import smtplib
from email.mime.text import MIMEText
from transformers import pipeline
from time import sleep
from celery import Celery
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
import json
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from transformers import pipeline

# Initialize the Hugging Face text generation model
generator = pipeline('text-generation', model='EleutherAI/gpt-neo-1.3B')

def get_credentials():
    credentials_dict = json.loads(os.environ.get('CREDENTIALS'))
    credentials = Credentials.from_authorized_user_info(credentials_dict)
    return credentials

def generate_email_content_with_huggingface(prompt_template, row_data):
    """Generates email content using Hugging Face model with dynamic data from row_data."""
    filled_prompt = prompt_template.format(**row_data)
    generated_content = generator(filled_prompt, max_length=200, num_return_sequences=1)
    return generated_content[0]['generated_text']


from .models import EmailStatus

@shared_task
def send_scheduled_emails(email_template, schedule_time, data_rows):
    print(f"Task started: schedule_time={schedule_time}, data_rows={len(data_rows)}")

    try:
        credentials = get_credentials()

        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())

        service = build("gmail", "v1", credentials=credentials)

        for row in data_rows:
            # Create or update the email status in the database
            email_status, created = EmailStatus.objects.get_or_create(
                email=row['Email'],
                defaults={'status': 'SCHEDULED', 'scheduled_time': now()}
            )

            # Generate personalized email content
            email_content = generate_email_content_with_huggingface(email_template, row)
            print(f"Generated email content: {email_content}")

            # Prepare the email message
            message = MIMEMultipart()
            message["to"] = row["Email"]
            message["from"] = "me"
            message["subject"] = f"Personalized Offer for {row['Company Name']}"
            message.attach(MIMEText(email_content, "plain"))

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

            # Send the email using Gmail API
            try:
                service.users().messages().send(userId="me", body={"raw": raw_message}).execute()
                print(f"Email sent successfully to {row['Email']}")

                # Update status to SENT
                email_status.status = 'SENT'
                email_status.sent_time = now()
                email_status.save()

            except Exception as email_error:
                print(f"Failed to send email to {row['Email']}: {str(email_error)}")

                # Update status to FAILED
                email_status.status = 'FAILED'
                email_status.error_message = str(email_error)
                email_status.save()

            # Throttle email sending
            sleep(schedule_time)
    except Exception as e:
        print(f"Error in sending scheduled emails: {str(e)}")



