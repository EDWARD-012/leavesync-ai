from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("accounts/logout/success/", views.logout_success, name="logout_success"),

    # Dashboards
    path("dashboard/", views.employee_dashboard, name="employee_dashboard"),
    path("dashboard/manager/", views.manager_dashboard, name="manager_dashboard"),
    path("dashboard/hr/", views.hr_dashboard, name="hr_dashboard"),
    path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"),

    # Leave management
    path("leave/apply/", views.apply_leave, name="apply_leave"),
    path("leave/pending/", views.pending_requests, name="pending_requests"),
    path("leave/history/", views.leave_history, name="leave_history"),

    path("leave/approve/<int:request_id>/", views.approve_leave, name="approve_leave"),
    path("leave/reject/<int:request_id>/", views.reject_leave, name="reject_leave"),
    path("leave/request-proof/<int:request_id>/", views.request_proof, name="request_proof"),
    path("leave/mark-proof/<int:request_id>/", views.mark_proof_provided, name="mark_proof_provided"),
    path("leave/upload-holidays/", views.upload_holidays, name="upload_holidays"),

    # Company management
    path("company/register/", views.register_company, name="register_company"),
    path("company/roles/", views.manage_company_roles, name="manage_company_roles"),
    path("company/users/", views.company_users, name="company_users"),

    path("api/calendar/", views.calendar_api, name="calendar_api"),

]
