from django.urls import path
from . import views

urlpatterns = [
    path('new/', views.create_complaint_view, name='create_complaint'),

    # staff URLs
    path('staff/tickets/', views.staff_ticket_list_view, name='staff_ticket_list'),
    path('staff/tickets/<str:ticket_id>/', views.staff_ticket_detail_view, name='staff_ticket_detail'),

    # leadership dashboard
    path('staff/dashboard/', views.dashboard_view, name='dashboard'),

    # customer feedback
    path('feedback/<str:ticket_id>/', views.feedback_view, name='ticket_feedback'),
]
