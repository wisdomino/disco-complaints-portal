# tickets/utils.py
from datetime import datetime
from django.core.mail import send_mail
from .models import Ticket


def generate_ticket_id():
    """
    Simple ticket format: DISCO-YYYY-XXXXXX
    Where XXXXXX is a zero-padded sequence.
    """
    year = datetime.now().year
    prefix = f"DISCO-{year}-"

    count = Ticket.objects.filter(ticket_id__startswith=prefix).count() + 1
    return f"{prefix}{count:06d}"


def send_acknowledgement_email(ticket):
    subject = f"Complaint Received - Ticket {ticket.ticket_id}"
    message = (
        f"Dear {ticket.customer.name},\n\n"
        f"We have received your complaint with Ticket ID: {ticket.ticket_id}.\n"
        f"Category: {ticket.category.name}\n"
        f"Description:\n{ticket.description}\n\n"
        "Our team will attend to it and keep you updated.\n\n"
        "Regards,\nYour DISCO"
    )
    send_mail(subject, message, None, [ticket.customer.email])


def send_escalation_email(ticket, to_staff):
    subject = f"Your Complaint {ticket.ticket_id} has been escalated"
    message = (
        f"Dear {ticket.customer.name},\n\n"
        f"Your complaint with Ticket ID {ticket.ticket_id} has been escalated "
        f"to {to_staff.user.get_full_name()} ({to_staff.role}).\n\n"
        "We will keep you updated on further progress.\n\n"
        "Regards,\nYour DISCO"
    )
    send_mail(subject, message, None, [ticket.customer.email])


def send_resolved_email(ticket):
    # Base URL for your app – in dev we use localhost, in prod set e.g. https://complaints.yourdisco.com
    base_url = getattr(settings, "SITE_BASE_URL", "http://127.0.0.1:8000")

    feedback_path = reverse("ticket_feedback", args=[ticket.ticket_id])
    feedback_link = f"{base_url}{feedback_path}"

    subject = f"Your Complaint {ticket.ticket_id} has been resolved"
    message = (
        f"Dear {ticket.customer.name},\n\n"
        f"Your complaint with Ticket ID {ticket.ticket_id} has been marked as resolved.\n"
        f"Please let us know if you are satisfied by clicking this link:\n{feedback_link}\n\n"
        "Regards,\nYour DISCO"
    )
    send_mail(subject, message, None, [ticket.customer.email])
