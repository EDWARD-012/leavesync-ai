from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from .models import Company, LeaveBalance, LeaveType, CompanyLeavePolicy, CompanyRoleDesignation

@receiver(user_signed_up)
def create_user_profile(request, user, **kwargs):
    email = (user.email or "").lower()
    domain = email.split("@")[-1] if "@" in email else None

    if domain:
        company, created = Company.objects.get_or_create(
            domain=domain,
            defaults={"name": domain.split(".")[0].capitalize(), "location": "Unknown", "is_verified": False},
        )
        user.company = company
        
        # Check if this email is designated for a specific role
        designation = CompanyRoleDesignation.objects.filter(
            company=company,
            email=email,
            is_active=True
        ).first()
        
        if designation:
            user.role = designation.role
        else:
            # Default to employee if not designated
            user.role = getattr(user, "role", "employee")
    else:
        # No company domain found, default to employee
        user.role = getattr(user, "role", "employee")

    user.save()

    # create balances from company policy or leavetype default
    if user.company:
        policies = CompanyLeavePolicy.objects.filter(company=user.company).select_related("leave_type")
        if policies.exists():
            for pol in policies:
                LeaveBalance.objects.get_or_create(
                    user=user, leave_type=pol.leave_type, defaults={"available_days": pol.days_per_year}
                )
        else:
            # fallback: use LeaveType.default_allocation
            for lt in LeaveType.objects.all():
                LeaveBalance.objects.get_or_create(user=user, leave_type=lt, defaults={"available_days": lt.default_allocation})
    else:
        # no company: fallback to global defaults
        for lt in LeaveType.objects.all():
            LeaveBalance.objects.get_or_create(user=user, leave_type=lt, defaults={"available_days": lt.default_allocation})
