from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Company, CompanyLeavePolicy, LeaveBalance, LeaveType, User

class Command(BaseCommand):
    help = "Reset / refresh leave balances according to company policies. Typically run yearly."

    def add_arguments(self, parser):
        parser.add_argument("--year", type=int, help="Year to reset for (defaults to current year)")

    def handle(self, *args, **options):
        year = options.get("year") or timezone.now().year
        self.stdout.write(f"Resetting leave balances for year {year} ...")
        companies = Company.objects.all()
        for company in companies:
            self.stdout.write(f" Processing company: {company.name}")
            policies = CompanyLeavePolicy.objects.filter(company=company).select_related("leave_type")
            users = User.objects.filter(company=company, is_active=True)
            if policies.exists():
                for user in users:
                    for pol in policies:
                        lb, created = LeaveBalance.objects.get_or_create(user=user, leave_type=pol.leave_type)
                        lb.available_days = pol.days_per_year
                        lb.save()
                self.stdout.write(f"  -> Reset balances for {users.count()} users.")
            else:
                # fallback to LeaveType defaults
                for user in users:
                    for lt in LeaveType.objects.all():
                        lb, created = LeaveBalance.objects.get_or_create(user=user, leave_type=lt)
                        lb.available_days = lt.default_allocation
                        lb.save()
                self.stdout.write(f"  -> Reset balances (fallback) for {users.count()} users.")
        self.stdout.write(self.style.SUCCESS("Leave balances reset complete."))
