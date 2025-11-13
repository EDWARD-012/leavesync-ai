from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import date, timedelta
from .models import User, LeaveRequest, LeaveType, LeaveBalance, Holiday, WorkWeek, Company, CompanyRoleDesignation
from .forms import LeaveRequestForm, HolidayUploadForm, CompanyRegistrationForm, RoleDesignationForm
from core.utils.ai_suggestions import suggest_best_leaves


# 🏠 Home Page
def home(request):
    return render(request, "home.html")


# 🔒 Logout Success Page (after AllAuth logout)
def logout_success(request):
    return render(request, "registration/logout.html")


# 👩‍💼 Employee Dashboard
from core.utils.ai_suggestions import suggest_best_leaves

@login_required
def employee_dashboard(request):
    balances = LeaveBalance.objects.filter(user=request.user)
    leave_requests = LeaveRequest.objects.filter(user=request.user).order_by("-applied_on")[:5]
    suggestions = suggest_best_leaves(request.user)
    return render(request, "dashboards/employee.html", {
        "balances": balances,
        "leave_requests": leave_requests,
        "suggestions": suggestions,
    })



# 👨‍💼 Manager Dashboard
@login_required
def manager_dashboard(request):
    if request.user.role != "manager":
        return redirect("employee_dashboard")

    # show only leaves for the same company
    requests = LeaveRequest.objects.filter(
        status="pending",
        user__company=request.user.company
    ).select_related("user", "leave_type").order_by("-applied_on")

    return render(request, "dashboards/manager.html", {"requests": requests})


# 👩‍💻 HR Dashboard
@login_required
def hr_dashboard(request):
    if request.user.role != "hr":
        return redirect("employee_dashboard")

    # HR can see all balances from their own company
    balances = LeaveBalance.objects.select_related("user", "leave_type").filter(
        user__company=request.user.company
    ).order_by("user__username")

    return render(request, "dashboards/hr.html", {"balances": balances})



# 🧑‍💼 Admin Dashboard (unchanged — sees everything)
@login_required
def admin_dashboard(request):
    if request.user.role != "admin":
        return redirect("employee_dashboard")

    stats = {
        "total_users": User.objects.count(),
        "pending": LeaveRequest.objects.filter(status="pending").count(),
        "approved": LeaveRequest.objects.filter(status="approved").count(),
        "rejected": LeaveRequest.objects.filter(status="rejected").count(),
    }

    all_requests = LeaveRequest.objects.select_related("user", "leave_type").order_by("-applied_on")
    all_users = User.objects.all().order_by("username")

    return render(request, "dashboards/admin.html", {
        "stats": stats,
        "all_requests": all_requests,
        "all_users": all_users,
    })


# 📝 Apply Leave
@login_required
def apply_leave(request):
    from core.utils.email_draft import generate_leave_email_draft, generate_fallback_email
    
    email_draft = None
    if request.method == "POST":
        if "generate_email" in request.POST:
            # Generate AI email draft
            leave_type = request.POST.get("leave_type", "")
            start_date_str = request.POST.get("start_date", "")
            end_date_str = request.POST.get("end_date", "")
            reason = request.POST.get("reason", "")
            
            if leave_type and start_date_str and end_date_str:
                try:
                    from datetime import datetime
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                    
                    leave_type_obj = LeaveType.objects.get(id=leave_type)
                    manager = User.objects.filter(
                        company=request.user.company, role="manager"
                    ).first()
                    manager_name = manager.get_full_name() if manager and manager.get_full_name() else "Manager"
                    
                    email_draft = generate_leave_email_draft(
                        leave_type_obj.name,
                        start_date,
                        end_date,
                        reason,
                        request.user.get_full_name() or request.user.username,
                        manager_name
                    )
                    
                    if not email_draft:
                        # AI generation failed, use enhanced fallback
                        email_draft = generate_fallback_email(
                            leave_type_obj.name,
                            start_date,
                            end_date,
                            reason,
                            request.user.get_full_name() or request.user.username,
                            manager_name
                        )
                        messages.info(
                            request, 
                            "AI email generation unavailable. Using enhanced template. "
                            "Please check OPENAI_API_KEY in settings if you want AI-generated emails."
                        )
                except Exception as e:
                    messages.error(request, f"Error generating email: {str(e)}")
                    # Still provide fallback
                    try:
                        email_draft = generate_fallback_email(
                            leave_type_obj.name,
                            start_date,
                            end_date,
                            reason,
                            request.user.get_full_name() or request.user.username,
                            manager_name
                        )
                    except:
                        pass
        
        if "submit_leave" in request.POST:
            form = LeaveRequestForm(request.POST)
            if form.is_valid():
                leave = form.save(commit=False)
                leave.user = request.user
                
                # Save email draft if provided
                email_draft_text = request.POST.get("email_draft", "").strip()
                if email_draft_text:
                    leave.email_draft = email_draft_text

                balance, created = LeaveBalance.objects.get_or_create(
                    user=request.user, 
                    leave_type=leave.leave_type,
                    defaults={"available_days": leave.leave_type.default_allocation}
                )

                if balance.available_days < leave.total_days:
                    messages.error(
                        request, 
                        f"Insufficient leave balance. You have {balance.available_days} days available for {leave.leave_type.name}, but requested {leave.total_days} days."
                    )
                else:
                    leave.save()
                    messages.success(request, "Leave request submitted successfully.")
                    return redirect("employee_dashboard")
            else:
                # If form is invalid, keep the email draft if it exists
                pass
        else:
            # For generate_email, create form with POST data to preserve values
            form = LeaveRequestForm(request.POST)
    else:
        form = LeaveRequestForm()
    
    return render(request, "leave/apply_leave.html", {
        "form": form,
        "email_draft": email_draft,
    })

# ⏳ Pending Requests (Manager/Admin/HR)
@login_required
def pending_requests(request):
    if request.user.role not in ["manager", "admin", "hr"]:
        return redirect("employee_dashboard")

    qs = LeaveRequest.objects.filter(status="pending").select_related("user", "leave_type")
    if request.user.role == "manager":
        qs = qs.filter(user__company=request.user.company)
    elif request.user.role == "hr":
        qs = qs.filter(user__company=request.user.company)

    requests = qs.order_by("-applied_on")
    return render(request, "leave/pending_requests.html", {"requests": requests})

# ✅ Approve Leave
@login_required
def approve_leave(request, request_id):
    if request.user.role not in ["manager", "admin", "hr"]:
        messages.error(request, "You don't have permission to approve leave requests.")
        return redirect("employee_dashboard")

    leave = get_object_or_404(LeaveRequest, id=request_id)
    
    # SECURITY: Prevent self-approval
    if leave.user == request.user:
        messages.error(request, "You cannot approve your own leave request. Please ask another HR/Manager to review it.")
        return redirect("pending_requests")
    
    # SECURITY: Ensure reviewer is from same company
    if request.user.company and leave.user.company != request.user.company:
        messages.error(request, "You can only approve leave requests from your own company.")
        return redirect("pending_requests")
    
    leave.status = "approved"
    leave.reviewed_by = request.user
    from django.utils import timezone
    leave.reviewed_on = timezone.now()
    leave.save()

    balance = LeaveBalance.objects.filter(user=leave.user, leave_type=leave.leave_type).first()
    if balance:
        balance.available_days = max(balance.available_days - leave.total_days, 0)
        balance.save()

    messages.success(request, f"Leave request approved for {leave.user.username}.")
    return redirect("pending_requests")


# ❌ Reject Leave
@login_required
def reject_leave(request, request_id):
    if request.user.role not in ["manager", "admin", "hr"]:
        messages.error(request, "You don't have permission to reject leave requests.")
        return redirect("employee_dashboard")

    leave = get_object_or_404(LeaveRequest, id=request_id)
    
    # SECURITY: Prevent self-rejection (though less critical, still good practice)
    if leave.user == request.user:
        messages.error(request, "You cannot reject your own leave request.")
        return redirect("pending_requests")
    
    # SECURITY: Ensure reviewer is from same company
    if request.user.company and leave.user.company != request.user.company:
        messages.error(request, "You can only reject leave requests from your own company.")
        return redirect("pending_requests")
    
    leave.status = "rejected"
    leave.reviewed_by = request.user
    from django.utils import timezone
    leave.reviewed_on = timezone.now()
    leave.save()
    messages.info(request, f"Leave request rejected for {leave.user.username}.")
    return redirect("pending_requests")


# 📎 Request Proof
@login_required
def request_proof(request, request_id):
    if request.user.role not in ["manager", "admin", "hr"]:
        messages.error(request, "You don't have permission to request proof.")
        return redirect("employee_dashboard")

    leave = get_object_or_404(LeaveRequest, id=request_id)
    leave.proof_requested = True
    leave.proof_requested_by = request.user
    from django.utils import timezone
    leave.proof_requested_on = timezone.now()
    leave.proof_provided = False
    leave.save()

    # Send notification email to employee
    from django.core.mail import send_mail
    from django.conf import settings
    try:
        send_mail(
            subject=f"Proof Required for Leave Request - {leave.leave_type.name}",
            message=(
                f"Dear {leave.user.get_full_name() or leave.user.username},\n\n"
                f"Your leave request for {leave.start_date} to {leave.end_date} requires additional proof/documentation.\n\n"
                f"Please provide the necessary documentation through the LeaveSync portal.\n\n"
                f"Requested by: {request.user.get_full_name() or request.user.username}\n"
                f"Date: {leave.proof_requested_on.strftime('%B %d, %Y at %I:%M %p')}\n\n"
                f"Thank you,\nLeaveSync Team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[leave.user.email],
            fail_silently=True,
        )
    except Exception:
        pass  # Email sending is optional

    messages.success(
        request,
        f"Proof requested from {leave.user.username}. They will be notified via email."
    )
    return redirect("pending_requests")


# ✅ Mark Proof as Provided
@login_required
def mark_proof_provided(request, request_id):
    leave = get_object_or_404(LeaveRequest, id=request_id)
    if leave.user != request.user:
        messages.error(request, "You can only mark proof for your own leave requests.")
        return redirect("employee_dashboard")

    leave.proof_provided = True
    leave.save()

    # Notify HR/Manager
    from django.core.mail import send_mail
    from django.conf import settings
    try:
        managers = User.objects.filter(
            company=request.user.company,
            role__in=["manager", "hr"]
        ).exclude(id=request.user.id)
        
        recipient_list = [m.email for m in managers if m.email]
        if recipient_list:
            send_mail(
                subject=f"Proof Provided - Leave Request by {request.user.username}",
                message=(
                    f"Dear Manager/HR,\n\n"
                    f"{request.user.get_full_name() or request.user.username} has provided proof for their leave request.\n\n"
                    f"Leave Details:\n"
                    f"- Type: {leave.leave_type.name}\n"
                    f"- Dates: {leave.start_date} to {leave.end_date}\n"
                    f"- Status: {leave.status.title()}\n\n"
                    f"Please review the proof in the LeaveSync portal.\n\n"
                    f"Thank you,\nLeaveSync Team"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=True,
            )
    except Exception:
        pass

    messages.success(request, "Proof marked as provided. HR/Manager will be notified.")
    return redirect("leave_history")


# 📜 Leave History (Employee)
@login_required
def leave_history(request):
    leaves = LeaveRequest.objects.filter(user=request.user).order_by("-applied_on")
    return render(request, "leave/leave_history.html", {"leaves": leaves})

from django.http import JsonResponse
from datetime import timedelta

@login_required
def calendar_data(request):
    user = request.user
    today = date.today()
    start = today.replace(day=1)
    end = (start + timedelta(days=40)).replace(day=1)  # next month

    leaves = LeaveRequest.objects.filter(
        user=user,
        start_date__lte=end,
        end_date__gte=start,
    )

    holidays = Holiday.objects.filter(
        company=user.company,
        date__gte=start,
        date__lte=end,
    )

    data = []

    for h in holidays:
        data.append({
            "title": h.name,
            "date": h.date.strftime("%Y-%m-%d"),
            "type": "holiday"
        })

    for l in leaves:
        d = l.start_date
        while d <= l.end_date:
            data.append({
                "title": f"Leave ({l.leave_type.name})",
                "date": d.strftime("%Y-%m-%d"),
                "type": "leave"
            })
            d += timedelta(days=1)

    return JsonResponse(data, safe=False)


from datetime import date, timedelta
from django.http import JsonResponse
from .models import Holiday, LeaveRequest, WorkWeek

@login_required
def calendar_api(request):
    user = request.user
    company = user.company
    month = int(request.GET.get("month", date.today().month))
    year = int(request.GET.get("year", date.today().year))

    start_date = date(year, month, 1)
    end_date = date(year, month + 1, 1) - timedelta(days=1) if month < 12 else date(year, 12, 31)

    holidays = Holiday.objects.filter(date__range=[start_date, end_date])
    leaves = LeaveRequest.objects.filter(user=user, start_date__lte=end_date, end_date__gte=start_date)
    workweek = WorkWeek.objects.filter(company=company).first()
    working_days = workweek.working_days if workweek else [1, 2, 3, 4, 5]

    data = []
    current = start_date
    all_days = {}

    while current <= end_date:
        day_type = "workday"
        tooltip = "Regular Working Day"

        if current.weekday() + 1 not in working_days:
            day_type, tooltip = "weekend", f"Weekend ({current.strftime('%A')})"
        else:
            holiday = holidays.filter(date=current).first()
            if holiday:
                day_type, tooltip = "holiday", f"🎉 {holiday.name}"
            else:
                leave = next((l for l in leaves if l.start_date <= current <= l.end_date), None)
                if leave:
                    day_type, tooltip = "leave", f"🟥 Your Leave ({leave.leave_type.name})"

        all_days[current] = {"date": current.isoformat(), "type": day_type, "tooltip": tooltip}
        current += timedelta(days=1)

    # 💡 Smart leave detection (bridge leaves across multiple workdays)
    ordered_days = sorted(all_days.keys())
    non_work_types = {"holiday", "weekend"}
    idx = 0
    while idx < len(ordered_days):
        current_day = ordered_days[idx]
        if all_days[current_day]["type"] != "workday":
            idx += 1
            continue

        segment_start_index = idx
        segment_end_index = idx

        while (
            segment_end_index + 1 < len(ordered_days)
            and all_days[ordered_days[segment_end_index + 1]]["type"] == "workday"
        ):
            segment_end_index += 1

        segment_start = ordered_days[segment_start_index]
        segment_end = ordered_days[segment_end_index]

        prev_day = segment_start - timedelta(days=1)
        next_day = segment_end + timedelta(days=1)

        if prev_day not in all_days or next_day not in all_days:
            idx = segment_end_index + 1
            continue

        prev_has_bridge = False
        next_has_bridge = False
        prev_has_holiday = False
        next_has_holiday = False

        scan_day = prev_day
        while scan_day in all_days and all_days[scan_day]["type"] in non_work_types:
            prev_has_bridge = True
            if all_days[scan_day]["type"] == "holiday":
                prev_has_holiday = True
            scan_day -= timedelta(days=1)

        scan_day = next_day
        while scan_day in all_days and all_days[scan_day]["type"] in non_work_types:
            next_has_bridge = True
            if all_days[scan_day]["type"] == "holiday":
                next_has_holiday = True
            scan_day += timedelta(days=1)

        has_holiday_neighbor = prev_has_holiday or next_has_holiday

        if prev_has_bridge and next_has_bridge and has_holiday_neighbor:
            smart_day = segment_start
            while smart_day <= segment_end:
                all_days[smart_day]["type"] = "smart_leave"
                all_days[smart_day]["tooltip"] = "💡 Smart Leave Suggestion: Take off to extend your break!"
                smart_day += timedelta(days=1)

        idx = segment_end_index + 1

    return JsonResponse(list(all_days.values()), safe=False)


# 📤 Upload Holidays (Manager/HR)
@login_required
def upload_holidays(request):
    if request.user.role not in ["manager", "hr", "admin"]:
        messages.error(request, "You don't have permission to upload holidays.")
        return redirect("employee_dashboard")
    
    if request.method == "POST":
        form = HolidayUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            from core.utils.holiday_parser import parse_holiday_file
            
            holidays_data = parse_holiday_file(file)
            
            if not holidays_data:
                messages.error(request, "Could not parse holidays from file. Please check the format.")
            else:
                created_count = 0
                updated_count = 0
                
                for name, holiday_date in holidays_data:
                    holiday, created = Holiday.objects.get_or_create(
                        company=request.user.company,
                        date=holiday_date,
                        defaults={"name": name}
                    )
                    if created:
                        created_count += 1
                    else:
                        holiday.name = name
                        holiday.save()
                        updated_count += 1
                
                messages.success(
                    request,
                    f"Successfully processed {len(holidays_data)} holidays: "
                    f"{created_count} created, {updated_count} updated."
                )
                return redirect("upload_holidays")
    else:
        form = HolidayUploadForm()
    
    # Show existing holidays
    existing_holidays = Holiday.objects.filter(
        company=request.user.company
    ).order_by("date")[:50]
    
    return render(request, "leave/upload_holidays.html", {
        "form": form,
        "holidays": existing_holidays,
    })


# 🏢 Company Registration
@login_required
def register_company(request):
    """Allow users to register their company"""
    if request.method == "POST":
        form = CompanyRegistrationForm(request.POST)
        if form.is_valid():
            # SECURITY: Check if user already has a company
            if request.user.company:
                messages.warning(request, "You are already associated with a company.")
                return redirect("employee_dashboard")
            
            # SECURITY: Verify email domain matches the company domain being registered
            user_email_domain = request.user.email.split("@")[-1].lower() if request.user.email else ""
            company_domain = form.cleaned_data.get("domain", "").lower().strip()
            
            if user_email_domain != company_domain:
                messages.error(
                    request,
                    f"Your email domain ({user_email_domain}) does not match the company domain ({company_domain}). "
                    f"You can only register a company that matches your email domain."
                )
                return redirect("register_company")
            
            company = form.save(commit=False)
            company.registered_by = request.user
            company.is_verified = False  # Requires admin verification
            company.save()
            
            # Assign the registering user as HR for this company (only if email domain matches)
            request.user.company = company
            if request.user.role == "employee":
                request.user.role = "hr"  # First registrant becomes HR (with domain verification)
            request.user.save()
            
            messages.success(
                request,
                f"Company '{company.name}' registered successfully! "
                f"Please designate HR/Manager emails below. "
                f"Note: Company verification may be required by admin."
            )
            return redirect("manage_company_roles")
    else:
        form = CompanyRegistrationForm()
    
    return render(request, "company/register_company.html", {"form": form})


# 👔 Manage Company Roles (HR/Manager Designations)
@login_required
def manage_company_roles(request):
    """Allow HR/Admin to designate email addresses as HR/Manager"""
    if request.user.role not in ["hr", "admin", "manager"]:
        messages.error(request, "You don't have permission to manage company roles.")
        return redirect("employee_dashboard")
    
    if not request.user.company:
        messages.warning(request, "You need to register a company first.")
        return redirect("register_company")
    
    company = request.user.company
    
    # Get existing designations
    designations = CompanyRoleDesignation.objects.filter(company=company).order_by("-designated_on")
    
    if request.method == "POST":
        form = RoleDesignationForm(request.POST)
        if form.is_valid():
            designation = form.save(commit=False)
            designation_email = form.cleaned_data.get("email", "").lower().strip()
            
            # SECURITY: Prevent self-designation
            if designation_email == request.user.email.lower():
                messages.error(
                    request,
                    "You cannot designate your own email address. "
                    "Please ask another HR/Admin to assign your role, or contact system administrator."
                )
                return redirect("manage_company_roles")
            
            # SECURITY: Verify email domain matches company domain
            email_domain = designation_email.split("@")[-1] if "@" in designation_email else ""
            if email_domain != company.domain.lower():
                messages.error(
                    request,
                    f"Email domain '{email_domain}' does not match company domain '{company.domain}'. "
                    f"Only emails from {company.domain} can be designated."
                )
                return redirect("manage_company_roles")
            
            # SECURITY: Prevent designating existing users (they should use manual assignment)
            existing_user = User.objects.filter(email__iexact=designation_email).first()
            if existing_user:
                messages.warning(
                    request,
                    f"User with email {designation_email} already exists. "
                    f"Please use 'Company Users' page to manually update their role instead."
                )
                return redirect("manage_company_roles")
            
            designation.company = company
            designation.designated_by = request.user
            designation.email = designation_email
            designation.save()
            
            messages.success(
                request,
                f"Role designation added: {designation.email} will be assigned as {designation.get_role_display()} when they sign up."
            )
            return redirect("manage_company_roles")
    else:
        form = RoleDesignationForm()
    
    # Get current users in company
    company_users = User.objects.filter(company=company).order_by("role", "username")
    
    return render(request, "company/manage_roles.html", {
        "form": form,
        "designations": designations,
        "company": company,
        "company_users": company_users,
    })


# 👥 View Company Users (HR/Manager)
@login_required
def company_users(request):
    """View all users in the company and manage their roles"""
    if request.user.role not in ["hr", "admin", "manager"]:
        messages.error(request, "You don't have permission to view company users.")
        return redirect("employee_dashboard")
    
    if not request.user.company:
        messages.warning(request, "You need to register a company first.")
        return redirect("register_company")
    
    company = request.user.company
    users = User.objects.filter(company=company).order_by("role", "username")
    
    if request.method == "POST" and "update_role" in request.POST:
        user_id = request.POST.get("user_id")
        new_role = request.POST.get("role")
        
        if user_id and new_role:
            try:
                user = User.objects.get(id=user_id, company=company)
                
                # SECURITY: Prevent self-role-change to HR/Manager/Admin
                if user == request.user and new_role in ["hr", "manager", "admin"]:
                    messages.error(
                        request,
                        "You cannot change your own role to HR/Manager/Admin. "
                        "Please ask another HR/Admin to update your role."
                    )
                    return redirect("company_users")
                
                # SECURITY: Only allow promoting to HR/Manager if current user is HR or Admin
                if new_role in ["hr", "manager", "admin"] and request.user.role not in ["hr", "admin"]:
                    messages.error(
                        request,
                        "Only HR or Admin can assign HR/Manager roles."
                    )
                    return redirect("company_users")
                
                old_role = user.role
                user.role = new_role
                user.save()
                messages.success(
                    request,
                    f"Updated {user.username}'s role from {old_role} to {new_role}."
                )
            except User.DoesNotExist:
                messages.error(request, "User not found.")
        
        return redirect("company_users")
    
    return render(request, "company/users.html", {
        "company": company,
        "users": users,
    })
