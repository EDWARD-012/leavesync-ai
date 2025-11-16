from allauth.account.adapter import DefaultAccountAdapter
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from .email_utils import send_email_via_brevo

class CustomAccountAdapter(DefaultAccountAdapter):

    def send_mail(self, template_prefix, email, context):
        """
        Override default SMTP sending.
        Use our Brevo API instead.
        """
        # Load templates
        html = render_to_string(f"{template_prefix}.html", context)

        subject = context.get("email_subject", "Verify your email")

        send_email_via_brevo(subject, html, email)
