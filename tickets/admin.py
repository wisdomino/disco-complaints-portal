from django.contrib import admin
from .models import Customer, Category, StaffUser, Ticket, TicketHistory


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'account_number', 'meter_number')
    search_fields = ('name', 'email', 'phone', 'account_number', 'meter_number')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'default_first_level_role')
    search_fields = ('name',)


@admin.register(StaffUser)
class StaffUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'department', 'region')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'role')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'customer', 'category', 'status',
                    'current_assigned_to', 'created_at', 'resolved_at')
    list_filter = ('status', 'category', 'created_at', 'resolved_at')
    search_fields = ('ticket_id', 'customer__name', 'customer__email')


@admin.register(TicketHistory)
class TicketHistoryAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'action_type', 'from_staff', 'to_staff', 'created_at')
    list_filter = ('action_type', 'created_at')