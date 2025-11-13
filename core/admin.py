from django.contrib import admin
from .models import User, Company, LeaveType, LeaveBalance, LeaveRequest, CompanyRoleDesignation

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "company", "is_active")
    list_filter = ("role", "company", "is_active")
    search_fields = ("username", "email")
    list_editable = ("role", "is_active")  # ✅ HR/Admin can assign roles easily

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "domain", "location")
    search_fields = ("name", "domain")

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "default_allocation")

@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ("user", "leave_type", "available_days")

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "leave_type", "status", "applied_on", "reviewed_by")
    list_filter = ("status", "leave_type")
    search_fields = ("user__username", "leave_type__name")

from django.contrib import admin
from .models import CompanyLeavePolicy

@admin.register(CompanyLeavePolicy)
class CompanyLeavePolicyAdmin(admin.ModelAdmin):
    list_display = ("company", "leave_type", "days_per_year")
    list_filter = ("company", "leave_type")
    search_fields = ("company__name", "leave_type__name")

@admin.register(CompanyRoleDesignation)
class CompanyRoleDesignationAdmin(admin.ModelAdmin):
    list_display = ("company", "email", "role", "is_active", "designated_on")
    list_filter = ("company", "role", "is_active")
    search_fields = ("email", "company__name")
    list_editable = ("is_active",)

