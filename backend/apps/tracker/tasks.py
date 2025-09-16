from celery import shared_task
from django.utils import timezone
from .models import Issue
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_overdue_reminders():
    today = timezone.localdate()
    overdue = Issue.objects.filter(due_date__lt=today).exclude(status="done")
    for issue in overdue:
        if issue.assigned_to and issue.assigned_to.email:
            send_mail(
                subject=f"[Reminder] Overdue issue: {issue.title}",
                message=f"The issue '{issue.title}' (project: {issue.project.name}) is overdue (due {issue.due_date}).",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[issue.assigned_to.email],
                fail_silently=True,
            )
