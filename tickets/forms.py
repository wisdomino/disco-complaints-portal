# tickets/forms.py

from django import forms
from .models import Category, StaffUser


class ComplaintForm(forms.Form):
    name = forms.CharField(max_length=150, label="Full Name")
    email = forms.EmailField(label="Email")
    phone = forms.CharField(max_length=20, label="Phone Number")
    account_number = forms.CharField(max_length=50, required=False)
    meter_number = forms.CharField(max_length=50, required=False)
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Select Complaint Category"
    )
    description = forms.CharField(
        widget=forms.Textarea,
        label="Complaint Details"
    )


class TicketStatusForm(forms.Form):
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]
    status = forms.ChoiceField(choices=STATUS_CHOICES)
    comment = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label="Comment / Update"
    )


class EscalationForm(forms.Form):
    to_staff = forms.ModelChoiceField(
        queryset=StaffUser.objects.all(),
        label="Escalate To"
    )
    comment = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label="Reason / Comment"
    )
class FeedbackForm(forms.Form):
    RATING_CHOICES = [
        (1, "1 - Very Dissatisfied"),
        (2, "2 - Dissatisfied"),
        (3, "3 - Neutral"),
        (4, "4 - Satisfied"),
        (5, "5 - Very Satisfied"),
    ]
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect,
        label="How satisfied are you with the resolution?"
    )
    comment = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label="Any additional comments?"
    )
