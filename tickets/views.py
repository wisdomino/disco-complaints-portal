# tickets/views.py
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages

from .forms import ComplaintForm
from .models import Customer, Ticket, StaffUser, TicketHistory
from .utils import generate_ticket_id, send_acknowledgement_email
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from .forms import ComplaintForm, TicketStatusForm, EscalationForm
from .utils import (
    generate_ticket_id,
    send_acknowledgement_email,
    send_escalation_email,
    send_resolved_email,
)
from .forms import ComplaintForm, TicketStatusForm, EscalationForm, FeedbackForm
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from django.utils import timezone


def feedback_view(request, ticket_id):
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)

    # Optionally: only allow feedback if resolved
    if ticket.status != 'RESOLVED':
        return render(request, "tickets/feedback_not_allowed.html", {"ticket": ticket})

    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            rating = int(form.cleaned_data['rating'])
            comment = form.cleaned_data['comment']

            ticket.satisfaction_rating = rating
            ticket.satisfaction_comment = comment
            ticket.save()

            return render(request, "tickets/feedback_thanks.html", {"ticket": ticket})
    else:
        form = FeedbackForm()

    return render(request, "tickets/feedback_form.html", {
        "ticket": ticket,
        "form": form,
    })

def home_view(request):
    return render(request, "tickets/home.html")


def create_complaint_view(request):
    if request.method == "POST":
        form = ComplaintForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            account_number = form.cleaned_data['account_number']
            meter_number = form.cleaned_data['meter_number']
            category = form.cleaned_data['category']
            description = form.cleaned_data['description']


            # 1. Get or create customer
            customer, created = Customer.objects.get_or_create(
                email=email,
                defaults={
                    'name': name,
                    'phone': phone,
                    'account_number': account_number,
                    'meter_number': meter_number,
                }
            )
            # Optional: update phone/account if changed
            if not created:
                customer.name = name
                customer.phone = phone
                if account_number:
                    customer.account_number = account_number
                if meter_number:
                    customer.meter_number = meter_number
                customer.save()

            # 2. Decide first assigned staff (for now: pick any staff with matching role)
            # Later we can make this smarter (by region, load, etc.)
            first_staff = StaffUser.objects.filter(
                role=category.default_first_level_role
            ).first()

            # 3. Create ticket
            ticket = Ticket.objects.create(
                ticket_id=generate_ticket_id(),
                customer=customer,
                category=category,
                description=description,
                current_assigned_to=first_staff,
                status='NEW',
            )

# Log initial assignment in history
            TicketHistory.objects.create(
                ticket=ticket,
                from_staff=None,
                to_staff=first_staff,
                action_type='ASSIGNED',
                comment="Ticket created and assigned automatically"
            )

            # TODO: send acknowledgement email here
            send_acknowledgement_email(ticket)

            # 4. Show success page/message
            return render(request, "tickets/complaint_success.html", {
                "ticket": ticket
            })
    else:
        form = ComplaintForm()

    return render(request, "tickets/complaint_form.html", {"form": form})

@login_required
def staff_ticket_list_view(request):
    # Get StaffUser linked to current logged-in user
    staff_user = get_object_or_404(StaffUser, user=request.user)
    tickets = Ticket.objects.filter(current_assigned_to=staff_user).order_by('-created_at')
    return render(request, "tickets/staff_ticket_list.html", {"tickets": tickets})


@login_required
def staff_ticket_detail_view(request, ticket_id):
    staff_user = get_object_or_404(StaffUser, user=request.user)
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)

    # Optional: ensure users only see tickets in their org rules.
    # For now we allow any logged-in staff to view any ticket.

    status_form = TicketStatusForm()
    escalation_form = EscalationForm()

    if request.method == "POST":
        if 'update_status' in request.POST:
            status_form = TicketStatusForm(request.POST)
            if status_form.is_valid():
                new_status = status_form.cleaned_data['status']
                comment = status_form.cleaned_data['comment']

                old_status = ticket.status
                ticket.status = new_status

                # If resolved, set resolved_at
                from django.utils import timezone
                if new_status == 'RESOLVED' and ticket.resolved_at is None:
                    ticket.resolved_at = timezone.now()
                ticket.save()

                # Log history
                TicketHistory.objects.create(
                    ticket=ticket,
                    from_staff=staff_user,
                    to_staff=staff_user,
                    action_type='STATUS_CHANGED' if new_status != 'RESOLVED' else 'RESOLVED',
                    comment=comment or f"Status changed from {old_status} to {new_status}"
                )

                # If resolved, send email to customer
                if new_status == 'RESOLVED':
                    send_resolved_email(ticket)

                messages.success(request, "Ticket status updated successfully.")
                return redirect('staff_ticket_detail', ticket_id=ticket.ticket_id)

        elif 'escalate' in request.POST:
            escalation_form = EscalationForm(request.POST)
            if escalation_form.is_valid():
                to_staff = escalation_form.cleaned_data['to_staff']
                comment = escalation_form.cleaned_data['comment']

                # Update ticket assignment and status
                ticket.current_assigned_to = to_staff
                ticket.status = 'ESCALATED'
                ticket.save()

                # Log history
                TicketHistory.objects.create(
                    ticket=ticket,
                    from_staff=staff_user,
                    to_staff=to_staff,
                    action_type='ESCALATED',
                    comment=comment
                )

                # Email customer about escalation
                send_escalation_email(ticket, to_staff)

                messages.success(request, f"Ticket escalated to {to_staff}.")
                return redirect('staff_ticket_detail', ticket_id=ticket.ticket_id)

    history = ticket.history.order_by('-created_at')

    context = {
        "ticket": ticket,
        "history": history,
        "status_form": status_form,
        "escalation_form": escalation_form,
    }
    return render(request, "tickets/staff_ticket_detail.html", context)

@login_required
def dashboard_view(request):
    if not request.user.is_staff and not request.user.is_superuser:
        return render(request, "tickets/not_authorized.html", status=403)

    # Filters from GET params
    status_filter = request.GET.get('status')
    start_date = request.GET.get('start_date')  # expected format: YYYY-MM-DD
    end_date = request.GET.get('end_date')

    tickets_qs = Ticket.objects.all()

    if status_filter:
        tickets_qs = tickets_qs.filter(status=status_filter)

    if start_date:
        tickets_qs = tickets_qs.filter(created_at__date__gte=start_date)
    if end_date:
        tickets_qs = tickets_qs.filter(created_at__date__lte=end_date)

    total_tickets = tickets_qs.count()

    status_counts = tickets_qs.values('status').annotate(count=Count('id'))
    category_counts = tickets_qs.values('category__name').annotate(count=Count('id'))

    resolved_tickets = tickets_qs.filter(resolved_at__isnull=False)
    avg_resolution = None
    if resolved_tickets.exists():
        durations = resolved_tickets.annotate(
            duration=ExpressionWrapper(
                F('resolved_at') - F('created_at'),
                output_field=DurationField()
            )
        ).aggregate(Avg('duration'))
        avg_resolution = durations['duration__avg']

    now = timezone.now()
    open_tickets = tickets_qs.filter(
        status__in=['NEW', 'IN_PROGRESS', 'ESCALATED']
    ).annotate(
        age=ExpressionWrapper(
            now - F('created_at'),
            output_field=DurationField()
        )
    ).order_by('-age')[:50]

    context = {
        "total_tickets": total_tickets,
        "status_counts": status_counts,
        "category_counts": category_counts,
        "avg_resolution": avg_resolution,
        "open_tickets": open_tickets,
        "status_filter": status_filter or "",
        "start_date": start_date or "",
        "end_date": end_date or "",
    }
    return render(request, "tickets/dashboard.html", context)

@login_required
def post_login_redirect_view(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('dashboard')
    return redirect('staff_ticket_list')

