from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.models import EmailAddress

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """Link social account to existing user with same verified email."""
        if sociallogin.is_existing:
            return

        email = sociallogin.account.extra_data.get("email")
        if not email:
            return

        try:
            email_address = EmailAddress.objects.get(email__iexact=email)
            user = email_address.user
            sociallogin.connect(request, user)
        except EmailAddress.DoesNotExist:
            pass
