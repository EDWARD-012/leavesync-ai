import calendar
import json
import os
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple

import requests
from django.conf import settings

from core.models import Holiday, LeaveBalance, LeaveRequest, WorkWeek

# Uses same model as email generation - can be overridden in .env
AI_MODEL = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")
SMART_TOOLTIP = "💡 Smart Leave Suggestion: Take off to extend your break!"


def suggest_best_leaves(user):
    """
    Fetch annual leave suggestions from the ChatGPT Responses API.
    Falls back to deterministic bridge-day suggestions if the API is unavailable.
    """
    snapshot = _build_year_snapshot(user)
    ai_suggestions = _fetch_ai_recommendations(snapshot)
    if ai_suggestions:
        return ai_suggestions

    return _fallback_suggestions(user)


# ---------------------------------------------------------------------------
#  Data preparation helpers
# ---------------------------------------------------------------------------
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

        months.append(
            {
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
            }
        )

    snapshot = {
        "company": getattr(user.company, "name", "N/A"),
        "user": user.username,
        "year_start": today.year,
        "span_years": span_years,
        "total_leave_balance": balance_total,
        "months": months,
    }
    return snapshot


def _get_working_days(user) -> List[int]:
    workweek = WorkWeek.objects.filter(company=user.company).first()
    return workweek.working_days if workweek and workweek.working_days else [1, 2, 3, 4, 5]


# ---------------------------------------------------------------------------
#  ChatGPT API integration
# ---------------------------------------------------------------------------
def _fetch_ai_recommendations(snapshot: Dict) -> Optional[List[Tuple[str, str]]]:
    api_key = getattr(settings, "OPENAI_API_KEY", None) or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    payload = {
        "model": AI_MODEL,
        "input": [
            {
                "role": "system",
                "content": (
                    "You are an HR leave-planning assistant. "
                    "Recommend strategic leave plans that help employees maximise longer breaks "
                    "while respecting existing company holidays and weekends."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Using the structured calendar data below, craft leave suggestions for each month. "
                    "Prefer short spans (1-3 days) that bridge holidays and weekends or form long breaks. "
                    "Return ONLY JSON that matches the provided schema.\n\n"
                    f"{json.dumps(snapshot, default=str)}"
                ),
            },
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "leave_suggestions",
                "schema": {
                    "type": "object",
                    "properties": {
                        "suggestions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "month": {"type": "string"},
                                    "ideas": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "start": {"type": "string"},
                                                "end": {"type": "string"},
                                                "reason": {"type": "string"},
                                            },
                                            "required": ["start", "end", "reason"],
                                        },
                                    },
                                    "notes": {"type": "string"},
                                },
                                "required": ["month", "ideas"],
                            },
                        }
                    },
                    "required": ["suggestions"],
                    "additionalProperties": False,
                },
            },
        },
        "temperature": 0.4,
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=20,
        )
        response.raise_for_status()
    except (requests.HTTPError, requests.ConnectionError, requests.Timeout):
        return None

    try:
        body = response.json()
        # The responses API returns a list of output items; each contains a list of content blocks.
        output = body.get("output", [])
        if not output:
            return None

        content_blocks = output[0].get("content", [])
        if not content_blocks:
            return None

        parsed = json.loads(content_blocks[0].get("text", "{}"))
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None

    return _normalise_ai_payload(parsed)


def _normalise_ai_payload(payload: Dict) -> Optional[List[Tuple[str, str]]]:
    results: List[Tuple[str, str]] = []
    for month_entry in payload.get("suggestions", []):
        month_label = month_entry.get("month")
        for idea in month_entry.get("ideas", []):
            start = idea.get("start")
            end = idea.get("end", start)
            reason = idea.get("reason", "").strip()
            if not (month_label and start and reason):
                continue
            descriptor = f"{month_label}: {start}"
            if end and end != start:
                descriptor += f" → {end}"
            results.append((descriptor, reason))
    return results or None


# ---------------------------------------------------------------------------
#  Fallback deterministic suggestions
# ---------------------------------------------------------------------------
def _fallback_suggestions(user, lookahead_days: int = 90) -> List[Tuple[str, str]]:
    today = date.today()
    working_days = set(_get_working_days(user))

    day_map: Dict[date, Dict[str, str]] = {}

    for offset in range(lookahead_days):
        d = today + timedelta(days=offset + 1)
        day_type = "workday"
        tooltip = "Regular Working Day"

        if (d.weekday() + 1) not in working_days:
            day_type = "weekend"
            tooltip = f"Weekend ({d.strftime('%A')})"
        else:
            holiday = Holiday.objects.filter(company=user.company, date=d).first()
            if holiday:
                day_type = "holiday"
                tooltip = f"🎉 {holiday.name}"
            else:
                leave = LeaveRequest.objects.filter(
                    user=user, start_date__lte=d, end_date__gte=d
                ).first()
                if leave:
                    day_type = "leave"
                    tooltip = f"🟥 Your Leave ({leave.leave_type.name})"

        day_map[d] = {"type": day_type, "tooltip": tooltip}

    _apply_bridge_detection(day_map)

    suggestions: List[Tuple[str, str]] = []
    for d, info in sorted(day_map.items()):
        if info["type"] == "smart_leave":
            label = d.strftime("%d %b %Y")
            suggestions.append((label, SMART_TOOLTIP))
    if not suggestions:
        # As an absolute fallback, encourage planning next month.
        target = today + timedelta(days=14)
        suggestions.append(
            (
                target.strftime("%d %b %Y"),
                "Consider taking a short break soon—no obvious bridges detected.",
            )
        )
    return suggestions


def _apply_bridge_detection(day_map: Dict[date, Dict[str, str]]) -> None:
    ordered_days = sorted(day_map.keys())
    non_work_types = {"holiday", "weekend"}
    idx = 0
    while idx < len(ordered_days):
        current_day = ordered_days[idx]
        if day_map[current_day]["type"] != "workday":
            idx += 1
            continue

        segment_start_idx = idx
        segment_end_idx = idx
        while (
            segment_end_idx + 1 < len(ordered_days)
            and day_map[ordered_days[segment_end_idx + 1]]["type"] == "workday"
        ):
            segment_end_idx += 1

        segment_start = ordered_days[segment_start_idx]
        segment_end = ordered_days[segment_end_idx]

        prev_day = segment_start - timedelta(days=1)
        next_day = segment_end + timedelta(days=1)

        if prev_day not in day_map or next_day not in day_map:
            idx = segment_end_idx + 1
            continue

        prev_has_bridge = False
        next_has_bridge = False
        prev_has_holiday = False
        next_has_holiday = False

        scan = prev_day
        while scan in day_map and day_map[scan]["type"] in non_work_types:
            prev_has_bridge = True
            if day_map[scan]["type"] == "holiday":
                prev_has_holiday = True
            scan -= timedelta(days=1)

        scan = next_day
        while scan in day_map and day_map[scan]["type"] in non_work_types:
            next_has_bridge = True
            if day_map[scan]["type"] == "holiday":
                next_has_holiday = True
            scan += timedelta(days=1)

        has_holiday_neighbor = prev_has_holiday or next_has_holiday

        if prev_has_bridge and next_has_bridge and has_holiday_neighbor:
            smart_day = segment_start
            while smart_day <= segment_end:
                day_map[smart_day]["type"] = "smart_leave"
                day_map[smart_day]["tooltip"] = SMART_TOOLTIP
                smart_day += timedelta(days=1)

        idx = segment_end_idx + 1
