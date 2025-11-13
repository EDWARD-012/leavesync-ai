import json
import os
from typing import Optional, Dict
import requests
from django.conf import settings
from datetime import date, timedelta


def generate_leave_email_draft(
    leave_type: str,
    start_date: date,
    end_date: date,
    reason: str,
    user_name: str,
    manager_name: str = "Manager"
) -> Optional[str]:
    """
    Generate a professional leave application email draft using ChatGPT API.
    The AI will enhance and professionally rephrase the reason provided by the employee.
    Returns None if API is unavailable.
    """
    api_key = getattr(settings, "OPENAI_API_KEY", None) or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY not found. Cannot generate AI email.")
        return None
    
    total_days = (end_date - start_date).days + 1
    
    payload = {
        "model": getattr(settings, "OPENAI_MODEL", "gpt-4o-mini"),
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a professional email assistant specializing in leave applications. "
                    "Your task is to:\n"
                    "1. Take the employee's reason and enhance it professionally\n"
                    "2. Rephrase it in a more formal, clear, and respectful manner\n"
                    "3. Add appropriate context and professionalism\n"
                    "4. Generate a complete, well-structured email that flows naturally\n"
                    "5. Make the reason sound more compelling and professional while keeping the core meaning\n"
                    "Use a formal but friendly tone. The email should be concise, clear, and professional."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Create a professional leave application email with these details:\n\n"
                    f"Employee Name: {user_name}\n"
                    f"Leave Type: {leave_type}\n"
                    f"Start Date: {start_date.strftime('%B %d, %Y')}\n"
                    f"End Date: {end_date.strftime('%B %d, %Y')}\n"
                    f"Total Days: {total_days}\n"
                    f"Manager Name: {manager_name}\n\n"
                    f"Employee's Original Reason (enhance this professionally and structure it well):\n{reason}\n\n"
                    f"Instructions:\n"
                    f"- Enhance and professionally rephrase the reason provided above\n"
                    f"- Make it sound more formal and compelling while keeping the essence\n"
                    f"- Write a complete email body (without subject line)\n"
                    f"- Include proper greeting, enhanced reason, and professional closing\n"
                    f"- Ensure the email is well-structured and flows naturally\n"
                    f"- Keep it concise but comprehensive"
                ),
            },
        ],
        "temperature": 0.7,
    }
    
    try:
        # Use chat completions API instead of responses API
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=15,
        )
        response.raise_for_status()
        
        body = response.json()
        choices = body.get("choices", [])
        if not choices:
            return None
        
        message = choices[0].get("message", {})
        email_body = message.get("content", "").strip()
        
        if email_body:
            return email_body
        return None
    
    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"API Error Details: {error_detail}")
            except:
                print(f"API Error Status: {e.response.status_code}")
        return None
    except Exception as e:
        print(f"Error generating email draft: {e}")
        import traceback
        traceback.print_exc()
        return None


def _enhance_reason_basic(reason: str) -> str:
    """Basic reason enhancement - fix common typos and improve grammar."""
    if not reason:
        return "Personal reasons"
    
    # Fix common typos
    reason = reason.replace("i ", "I ").replace("i'm", "I'm").replace("i'", "I'")
    reason = reason.replace(" a'm ", " am ").replace(" a'm", " am")
    reason = reason.replace(" lave", " leave").replace("lave", "leave")
    
    # Capitalize first letter
    if reason and reason[0].islower():
        reason = reason[0].upper() + reason[1:]
    
    # Add period if missing
    if reason and not reason.endswith(('.', '!', '?')):
        reason = reason + "."
    
    return reason


def generate_fallback_email(
    leave_type: str,
    start_date: date,
    end_date: date,
    reason: str,
    user_name: str,
    manager_name: str = "Manager"
) -> str:
    """Generate a simple fallback email if AI is unavailable."""
    total_days = (end_date - start_date).days + 1
    
    # Enhance reason with basic fixes
    enhanced_reason = _enhance_reason_basic(reason)
    
    # Create a more professional reason if the original is too casual
    if len(reason.strip()) < 10 or reason.lower() in ["i am on leave", "i'm on leave", "on leave"]:
        if leave_type.lower() == "sick leave":
            enhanced_reason = "I am unwell and require medical attention and rest."
        elif leave_type.lower() == "casual leave":
            enhanced_reason = "I need to attend to personal matters that require my attention."
        else:
            enhanced_reason = "I need to take time off for personal reasons."
    
    email = f"""Dear {manager_name},

I am writing to request {leave_type} leave from {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')} ({total_days} day{'s' if total_days > 1 else ''}).

Reason: {enhanced_reason}

I have ensured that my work responsibilities will be covered during my absence. I will be available for any urgent matters via email.

Thank you for considering my request.

Best regards,
{user_name}"""
    
    return email

