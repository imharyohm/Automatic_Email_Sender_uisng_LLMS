from django.db import models

class EmailStatus(models.Model):
    STATUS_CHOICES = [
        ('SENT', 'Sent'),
        ('PENDING', 'Pending'),
        ('SCHEDULED', 'Scheduled'),
        ('FAILED', 'Failed'),
    ]

    email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    scheduled_time = models.DateTimeField(null=True, blank=True)
    sent_time = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)

class EmailTracking(models.Model):
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('scheduled', 'Scheduled'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
    ]
    
    DELIVERY_STATUS_CHOICES = [
        ('delivered', 'Delivered'),
        ('opened', 'Opened'),
        ('bounced', 'Bounced'),
        ('failed', 'Failed'),
    ]
    
    email = models.EmailField()
    company_name = models.CharField(max_length=100)
    email_status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES, null=True, blank=True)
    opened = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.status}"
