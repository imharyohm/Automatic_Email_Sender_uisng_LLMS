from django.http import JsonResponse
from .models import EmailSchedule  # Import the EmailSchedule model
from .tasks import send_scheduled_emails  # Import the Celery task to send emails
from django.views.decorators.csrf import csrf_exempt  # Import the CSRF exemption decorator
import json
from datetime import datetime
from django.http import JsonResponse
from .models import EmailStatus
from django.db.models import Count
from django.http import JsonResponse
from mainapp.models import EmailTracking
# Create a view to handle scheduling email requests
@csrf_exempt
def schedule_emails(request):
    if request.method == "POST":
        try:
            # Log the incoming request data for debugging
            print("Request Body:", request.body)
            
            # Parse the incoming JSON data
            data = json.loads(request.body)
            email_content = data.get("email_content")
            schedule_time = data.get("schedule_time")
            data_rows = data.get("data_rows")

            # Check if essential fields are missing
            if not email_content:
                return JsonResponse({"status": "error", "message": "Email content is required."}, status=400)

            if not schedule_time:
                return JsonResponse({"status": "error", "message": "Schedule time is required."}, status=400)

            if not data_rows or len(data_rows) == 0:
                return JsonResponse({"status": "error", "message": "Data rows cannot be empty."}, status=400)

            # Process the scheduling task (perhaps saving to the database or sending emails)
            
            print("hellooo")# Convert schedule_time to seconds if needed (e.g., for batch intervals)
            schedule_time_seconds = int(schedule_time)

            # Schedule the task using Celery
            send_scheduled_emails.apply_async(
                args=[email_content, schedule_time_seconds, data_rows]
            )

            return JsonResponse({"status": "success", "message": "Scheduling initiated."})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)


def get_email_analytics(request):
    """
    API to get real-time analytics for sent emails.
    """
    try:
        total_emails = EmailStatus.objects.count()
        emails_sent = EmailStatus.objects.filter(status='SENT').count()
        emails_pending = EmailStatus.objects.filter(status='PENDING').count()
        emails_scheduled = EmailStatus.objects.filter(status='SCHEDULED').count()
        emails_failed = EmailStatus.objects.filter(status='FAILED').count()

        response = {
            "total_emails": total_emails,
            "emails_sent": emails_sent,
            "emails_pending": emails_pending,
            "emails_scheduled": emails_scheduled,
            "emails_failed": emails_failed,
        }

        return JsonResponse(response, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

def get_email_tracking_data(request):
    """API to fetch email tracking metrics."""
    delivered = EmailTracking.objects.filter(status='delivered').count()
    opened = EmailTracking.objects.filter(status='open').count()
    bounced = EmailTracking.objects.filter(status='bounce').count()
    failed = EmailTracking.objects.filter(status='failed').count()

    data = {
        "delivered": delivered,
        "opened": opened,
        "bounced": bounced,
        "failed": failed
    }
    return JsonResponse(data)

def get_email_status(request):
    """API to fetch email sending status and delivery status."""
    email_data = EmailTracking.objects.all()

    email_status_data = []
    for email in email_data:
        email_status_data.append({
            "company_name": email.company_name,
            "email": email.email,
            "email_status": email.email_status,
            "delivery_status": email.delivery_status,
            "opened": email.opened
        })
    
    return JsonResponse({"emails": email_status_data})
