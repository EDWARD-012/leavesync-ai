from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date

# Shared role choices for users and designations
ROLE_CHOICES = (
    ("employee", "Employee"),
    ("manager", "Manager"),
    ("hr", "HR"),
    ("admin", "Admin"),
)


# 🏢 Company Model
class Company(models.Model):
    name = models.CharField(max_length=100)
    domain = models.CharField(max_length=100, unique=True)  # e.g. "tcs.com"
    location = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False, help_text="Company is properly registered and verified")
    registered_by = models.ForeignKey(
        "core.User", related_name="registered_companies", null=True, blank=True, on_delete=models.SET_NULL
    )
    registered_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.location})"
    
    def get_hr_managers(self):
        """Get all HR and Manager users for this company"""
        return User.objects.filter(company=self, role__in=["hr", "manager"])


# 👤 Custom User Model
class User(AbstractUser):
    ROLE_CHOICES = ROLE_CHOICES
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="employee")
    department = models.CharField(max_length=100, blank=True)
    contact = models.CharField(max_length=20, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


# 🌴 Leave Type
class LeaveType(models.Model):
    name = models.CharField(max_length=50)
    default_allocation = models.IntegerField(default=12)

    def __str__(self):
        return self.name


# 💰 Leave Balance
class LeaveBalance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    available_days = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.leave_type.name} ({self.available_days})"


# 📅 Leave Request
class LeaveRequest(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True)
    email_draft = models.TextField(blank=True, help_text="AI-generated email draft sent by employee")
    proof_requested = models.BooleanField(default=False)
    proof_requested_by = models.ForeignKey(
        User, related_name="proof_requests", null=True, blank=True, on_delete=models.SET_NULL
    )
    proof_requested_on = models.DateTimeField(null=True, blank=True)
    proof_provided = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    applied_on = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        User, related_name="reviewer", null=True, blank=True, on_delete=models.SET_NULL
    )
    reviewed_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.leave_type.name} ({self.status})"

    @property
    def total_days(self):
        return (self.end_date - self.start_date).days + 1
    

# add near Company, LeaveType, LeaveBalance
class CompanyLeavePolicy(models.Model):
    company = models.ForeignKey("Company", on_delete=models.CASCADE, related_name="leave_policies")
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    days_per_year = models.IntegerField(default=0)  # how many days this company gives for this leave type

    class Meta:
        unique_together = ("company", "leave_type")

    def __str__(self):
        return f"{self.company.name} - {self.leave_type.name}: {self.days_per_year}"



from django.db import models
from datetime import date

class WorkWeek(models.Model):
    company = models.OneToOneField("Company", on_delete=models.CASCADE)
    # 1 = Monday, 7 = Sunday
    working_days = models.JSONField(default=list)  # e.g. [1, 2, 3, 4, 5] or [1,2,3,4,5,6]

    def __str__(self):
        return f"{self.company.name} - {len(self.working_days)} day week"


class Holiday(models.Model):
    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    date = models.DateField()
    name = models.CharField(max_length=100)
    is_optional = models.BooleanField(default=False)
    recurring = models.BooleanField(default=False)  # repeats every year

    def __str__(self):
        return f"{self.name} ({self.date})"

    def occurs_this_year(self):
        """Return this holiday date adjusted for current year if recurring."""
        if self.recurring:
            return self.date.replace(year=date.today().year)
        return self.date


# 👔 Company Admin/Designated Roles
class CompanyRoleDesignation(models.Model):
    """Designate specific email addresses as HR/Manager for a company"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="role_designations")
    email = models.EmailField(help_text="Email address that should be assigned this role")
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="employee",
        help_text="Role to assign when this email signs up"
    )
    designated_by = models.ForeignKey(
        "core.User", related_name="designations_made", null=True, blank=True, on_delete=models.SET_NULL
    )
    designated_on = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("company", "email")
        verbose_name = "Role Designation"
        verbose_name_plural = "Role Designations"

    def __str__(self):
        return f"{self.email} → {self.role} at {self.company.name}"


