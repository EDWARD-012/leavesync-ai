from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError
from datetime import date

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        import core.signals
        from .models import LeaveType, Company, WorkWeek, Holiday

        try:
            defaults = [
                ("Casual Leave", 12),
                ("Sick Leave", 10),
                ("Earned Leave", 15),
            ]
            for name, days in defaults:
                LeaveType.objects.get_or_create(name=name, defaults={"default_allocation": days})

            # Create workweek for each company (Mon-Fri default)
            for comp in Company.objects.all():
                WorkWeek.objects.get_or_create(company=comp, defaults={"working_days": [1,2,3,4,5]})

            # Add recurring fixed holidays
            fixed_holidays = [
                # 🇮🇳 National Holidays
                ("New Year’s Day", date(2025, 1, 1)),
                ("Republic Day", date(2025, 1, 26)),
                ("Independence Day", date(2025, 8, 15)),
                ("Gandhi Jayanti", date(2025, 10, 2)),
                ("Christmas Day", date(2025, 12, 25)),

                # 🌸 Major Festival Holidays (widely followed in Indian corporates)
                ("Holi", date(2025, 3, 14)),  # change date each year as per calendar
                ("Good Friday", date(2025, 4, 18)),
                ("Eid al-Fitr", date(2025, 3, 31)),
                ("Eid al-Adha (Bakrid)", date(2025, 6, 7)),
                ("Raksha Bandhan", date(2025, 8, 9)),
                ("Janmashtami", date(2025, 8, 16)),
                ("Ganesh Chaturthi", date(2025, 8, 27)),
                ("Mahatma Gandhi Jayanti", date(2025, 10, 2)),  # duplicate safety
                ("Dussehra (Vijaya Dashami)", date(2025, 10, 2)), # same week
                ("Diwali", date(2025, 10, 20)),
                ("Govardhan Puja", date(2025, 10, 21)),
                ("Bhai Dooj", date(2025, 10, 22)),
                ("Guru Nanak Jayanti", date(2025, 11, 5)),

                # 🌍 Optional / Regional (commonly given in MNCs)
                ("Makar Sankranti / Pongal", date(2025, 1, 14)),
                ("Mahashivratri", date(2025, 2, 26)),
                ("Ram Navami", date(2025, 4, 6)),
                ("Buddha Purnima", date(2025, 5, 12)),
                ("Onam", date(2025, 9, 14)),
                ("Christmas Eve", date(2025, 12, 24)),
            ]

            for comp in Company.objects.all():
                for name, d in fixed_holidays:
                    Holiday.objects.get_or_create(
                        company=comp,
                        name=name,
                        date=d,
                        defaults={"recurring": True}
                    )
        except (OperationalError, ProgrammingError):
            pass
