import calendar
import json
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple

from django.conf import settings
import google.generativeai as genai

from core.models import Holiday, LeaveBalance, LeaveRequest, WorkWeek

# Gemini API configuration
GEMINI_API_KEY = getattr(settings, "GEMINI_API_KEY", None)
GEMINI_MODEL = getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

SMART_TOOLTIP = "💡 Smart Leave Suggestion: Take off to extend your break!"


# -----------------------------------------------------
# PUBLIC FUNCTION
# -----------------------------------------------------
def suggest_best_leaves(user):
    """
    Try AI-powered smart leave suggestions using Gemini.
    Fallback to deterministic pattern suggestions if Gemini unavailable.
    """
    snapshot = _build_year_snapshot(user)
    ai_suggestions = _fetch_ai_recommendations(snapshot)
    if ai_suggestions:
        return ai_suggestions

    return _fallback_suggestions(user)


# -----------------------------------------------------
# DATA SNAPSHOT (SAME AS YOU ALREADY HAVE)
# -----------------------------------------------------
def _build_year_snapshot(user, span_years: int = 1) -> Dict:
    today = date.today()
    working_days = _get_working_days(user)
    balance_total = sum(
        LeaveBalance.objects.filter(user=user).values_list("available_days", flat=True)
    )

    months: List[Dict] = []
    for offset in range(span_years * 12):
        target_month = (today.month - 1 + offset) % 12 + 1
        target_year = today.year + (today.month - 1 + offset) // 12

        start = date(target_year, target_month, 1)
        end = date(target_year, target_month, calendar.monthrange(target_year, target_month)[1])

        holidays = Holiday.objects.filter(
            company=user.company, date__range=(start, end)
        ).order_by("date")

        leaves = LeaveRequest.objects.filter(
            user=user, start_date__lte=end, end_date__gte=start
        ).order_by("start_date")

        months.append({
            "label": start.strftime("%B %Y"),
            "year": target_year,
            "month": target_month,
            "working_days": working_days,
            "holidays": [
                {"date": h.date.isoformat(), "name": h.name, "is_optional": h.is_optional}
                for h in holidays
            ],
            "existing_leaves": [
                {
                    "start": lr.start_date.isoformat(),
                    "end": lr.end_date.isoformat(),
                    "type": lr.leave_type.name,
                    "status": lr.status,
                }
                for lr in leaves
            ],
        })

    return {
        "company": getattr(user.company, "name", "N/A"),
        "user": user.username,
        "year_start": today.year,
        "span_years": span_years,
        "total_leave_balance": balance_total,
        "months": months,
    }


def _get_working_days(user) -> List[int]:
    workweek = WorkWeek.objects.filter(company=user.company).first()
    return workweek.working_days if workweek else [1, 2, 3, 4, 5]


# -----------------------------------------------------
# 🌟 GEMINI AI RECOMMENDATION ENGINE
# -----------------------------------------------------
def _fetch_ai_recommendations(snapshot: Dict) -> Optional[List[Tuple[str, str]]]:
    if not GEMINI_API_KEY:
        return None

    prompt = f"""
You are an AI leave optimization assistant.

Using this structured calendar JSON:
{json.dumps(snapshot, indent=2)}

Generate ≤ 5 recommended leave ideas in JSON ONLY, format:
{{
  "suggestions": [
     {{
        "month": "Month Name",
        "ideas": [
           {{
             "start": "YYYY-MM-DD",
             "end": "YYYY-MM-DD",
             "reason": "brief explanation"
           }}
        ]
     }}
  ]
}}
"""

    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)

        if not response or not response.text:
            return None

        data = json.loads(response.text)
        return _normalize_ai_payload(data)

    except Exception:
        return None


def _normalize_ai_payload(payload: Dict):
    results = []
    for month_entry in payload.get("suggestions", []):
        month = month_entry.get("month")
        for idea in month_entry.get("ideas", []):
            start = idea.get("start")
            end = idea.get("end", start)
            reason = idea.get("reason", "")
            title = f"{month}: {start}" + (f" → {end}" if end != start else "")
            results.append((title, reason))
    return results or None


# -----------------------------------------------------
# FALLBACK (unchanged)
# -----------------------------------------------------
def _fallback_suggestions(user, lookahead_days: int = 90):
    today = date.today()
    working_days = set(_get_working_days(user))

    # ----------------------------
    # 1️⃣ PREFETCH EVERYTHING IN ONE QUERY
    # ----------------------------
    end_date = today + timedelta(days=lookahead_days)

    holidays = set(
        Holiday.objects.filter(
            company=user.company,
            date__range=(today, end_date)
        ).values_list("date", flat=True)
    )

    # Prefetch all leave ranges for the user
    leave_ranges = list(
        LeaveRequest.objects.filter(
            user=user,
            start_date__lte=end_date,
            end_date__gte=today
        ).values_list("start_date", "end_date")
    )

    # Convert leave ranges into a set of all dates the user is on leave
    leave_days = set()
    for start, end in leave_ranges:
        d = start
        while d <= end:
            leave_days.add(d)
            d += timedelta(days=1)

    # ----------------------------
    # 2️⃣ BUILD DAY MAP WITHOUT EXTRA QUERIES
    # ----------------------------
    day_map = {}
    for offset in range(lookahead_days):
        d = today + timedelta(days=offset + 1)

        if d in leave_days:
            day_type = "leave"
        elif d in holidays:
            day_type = "holiday"
        elif (d.weekday() + 1) not in working_days:
            day_type = "weekend"
        else:
            day_type = "workday"

        day_map[d] = {"type": day_type}

    # Detect bridge days
    _apply_bridge_detection(day_map)

    # ----------------------------
    # 3️⃣ COLLECT SUGGESTIONS
    # ----------------------------
    suggestions = [
        (d.strftime("%d %b %Y"), SMART_TOOLTIP)
        for d, v in day_map.items()
        if v["type"] == "smart_leave"
    ]

    if not suggestions:
        target = today + timedelta(days=14)
        suggestions.append((target.strftime("%d %b %Y"), "Consider planning a break soon."))

    return suggestions


def _apply_bridge_detection(day_map):
    ordered = sorted(day_map.keys())
    non_work = {"holiday", "weekend"}
    i = 0

    while i < len(ordered):
        d = ordered[i]
        if day_map[d]["type"] != "workday":
            i += 1
            continue

        start = end = i
        while end + 1 < len(ordered) and day_map[ordered[end + 1]]["type"] == "workday":
            end += 1

        left = ordered[start] - timedelta(days=1)
        right = ordered[end] + timedelta(days=1)

        left_non = left in day_map and day_map[left]["type"] in non_work
        right_non = right in day_map and day_map[right]["type"] in non_work

        if left_non and right_non:
            for j in range(start, end + 1):
                day_map[ordered[j]] = {
                    "type": "smart_leave",
                    "tooltip": SMART_TOOLTIP,
                }

        i = end + 1
