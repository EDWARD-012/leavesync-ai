from django import forms
from .models import LeaveRequest, Company, CompanyRoleDesignation

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ["leave_type", "start_date", "end_date", "reason"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "reason": forms.Textarea(attrs={"rows": 4, "placeholder": "Enter your reason for leave..."}),
        }

class HolidayUploadForm(forms.Form):
    file = forms.FileField(
        label="Upload Holiday File",
        help_text="Upload XLSX or PDF file containing holiday calendar",
        widget=forms.FileInput(attrs={"accept": ".xlsx,.xls,.pdf"})
    )


class CompanyRegistrationForm(forms.ModelForm):
    """Form for companies to register themselves"""
    class Meta:
        model = Company
        fields = ["name", "domain", "location"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Company Name", "class": "form-control"}),
            "domain": forms.TextInput(attrs={"placeholder": "example.com", "class": "form-control"}),
            "location": forms.TextInput(attrs={"placeholder": "City, Country", "class": "form-control"}),
        }
        help_texts = {
            "domain": "Enter your company email domain (e.g., 'acme.com'). Users signing up with emails from this domain will be automatically assigned to your company.",
        }

    def clean_domain(self):
        domain = self.cleaned_data.get("domain")
        if domain:
            domain = domain.lower().strip()
            # Remove http://, https://, www. if present
            domain = domain.replace("http://", "").replace("https://", "").replace("www.", "")
            # Remove trailing slash
            domain = domain.rstrip("/")
        return domain


class RoleDesignationForm(forms.ModelForm):
    """Form to designate email addresses as HR/Manager"""
    class Meta:
        model = CompanyRoleDesignation
        fields = ["email", "role"]
        widgets = {
            "email": forms.EmailInput(attrs={"placeholder": "employee@company.com", "class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-control"}),
        }
        help_texts = {
            "email": "Email address that should be assigned this role when they sign up",
            "role": "Role to assign to this email address",
        }
