import os
from datetime import date
from typing import Optional
from django.conf import settings
import google.generativeai as genai


# -------------------------------------------------------------------
# Gemini Configuration
# -------------------------------------------------------------------
GEMINI_API_KEY = getattr(settings, "GEMINI_API_KEY", None)
GEMINI_MODEL = getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


# -------------------------------------------------------------------
# AI Leave Email Generator
# -------------------------------------------------------------------
def generate_leave_email_draft(
    leave_type: str,
    start_date: date,
    end_date: date,
    reason: str,
    user_name: str,
    manager_name: str = "Manager"
) -> Optional[str]:
    """
    Generate a polished HR-grade professional leave application email.
    Uses Gemini. Returns None if AI fails.
    """

    if not GEMINI_API_KEY:
        print("⚠ Gemini API key missing — skipping AI generation.")
        return None

    total_days = (end_date - start_date).days + 1

    prompt = f"""
You are an expert HR communication assistant specializing in writing highly professional,
clear, polite workplace leave application emails.

Rewrite and enhance the user's informal reason into a polished, formal HR-compliant reason.

Write **ONLY the email body**, without subject, exactly in this structure:

1. Greeting
2. Short introduction
3. Professionally enhanced reason (very polished)
4. Mention dates clearly and accurately
5. Assurance of responsibility & availability
6. Closing line + signature

Tone:
- Professional
- Polite
- Crisp
- Zero grammar mistakes
- No exaggeration
- No unnecessary emotional sentences

Employee Data:
- Employee Name: {user_name}
- Manager Name: {manager_name}
- Leave Type: {leave_type}
- Start Date: {start_date.strftime('%B %d, %Y')}
- End Date: {end_date.strftime('%B %d, %Y')}
- Total Days: {total_days}
- Employee's Original Reason: "{reason}"

Now generate a highly polished, HR-approved leave application email body.
"""

    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)

        if not response or not response.text:
            return None

        email_text = response.text.strip()

        # Remove accidental markdown formatting if Gemini adds it
        email_text = email_text.replace("**", "").replace("*", "")

        return email_text

    except Exception as e:
        print("❗ Gemini email generation failed:", e)
        return None


# -------------------------------------------------------------------
# Minimal Professional Fallback (No AI)
# -------------------------------------------------------------------
def enhance_reason_basic(reason: str) -> str:
    """Small grammar fixes when AI is unavailable."""
    if not reason or reason.strip() == "":
        return "I have an important personal matter that requires my attention."

    text = reason.strip()

    # Capitalize first letter
    if text[0].islower():
        text = text[0].upper() + text[1:]

    # Add period
    if not text.endswith((".", "!", "?")):
        text += "."

    # Common typo fixes
    text = text.replace(" i ", " I ").replace("i'm", "I'm")

    return text


def generate_fallback_email(
    leave_type: str,
    start_date: date,
    end_date: date,
    reason: str,
    user_name: str,
    manager_name: str = "Manager"
):
    """
    Simple clean fallback email when AI is unavailable.
    Still formal and professional.
    """

    total_days = (end_date - start_date).days + 1
    enhanced_reason = enhance_reason_basic(reason)

    return f"""
Dear {manager_name},

I am writing to request {leave_type.lower()} from {start_date.strftime('%B %d, %Y')} \
to {end_date.strftime('%B %d, %Y')} ({total_days} day{'s' if total_days > 1 else ''}).

Reason: {enhanced_reason}

I will ensure that all responsibilities are managed appropriately during my absence and
will remain reachable for any urgent communication.

Thank you for considering my request.

Sincerely,
{user_name}
""".strip()
