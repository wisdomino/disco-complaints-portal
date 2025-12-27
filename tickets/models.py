from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    meter_number = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.account_number or self.phone})"


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    # e.g. "Billing Officer", "Feeder Engineer", "RPD Officer"
    default_first_level_role = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class StaffUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role}"


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('IN_PROGRESS', 'In Progress'),
        ('ESCALATED', 'Escalated'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]

    ticket_id = models.CharField(max_length=30, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    current_assigned_to = models.ForeignKey(
        StaffUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_tickets'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    satisfaction_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    satisfaction_comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.ticket_id


class TicketHistory(models.Model):
    ACTION_CHOICES = [
        ('ASSIGNED', 'Assigned'),
        ('ESCALATED', 'Escalated'),
        ('COMMENTED', 'Commented'),
        ('STATUS_CHANGED', 'Status Changed'),
        ('RESOLVED', 'Resolved'),
    ]

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='history')
    from_staff = models.ForeignKey(
        StaffUser,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='actions_from'
    )
    to_staff = models.ForeignKey(
        StaffUser,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='actions_to'
    )
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ticket.ticket_id} - {self.action_type} - {self.created_at}"