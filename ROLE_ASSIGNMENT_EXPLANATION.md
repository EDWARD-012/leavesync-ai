# Role Assignment Logic Explanation

## How User Roles Are Assigned in LeaveSync

### Overview
When a user signs up (via Google OAuth or regular signup), the system automatically assigns them to a company and assigns a role based on predefined designations.

### Step-by-Step Process

#### 1. **User Signs Up**
- User signs up with Google OAuth or regular email/password
- System extracts email domain (e.g., "john@acme.com" → domain: "acme.com")

#### 2. **Company Assignment**
```
Email: john@acme.com
↓
Extract Domain: acme.com
↓
Find or Create Company with domain="acme.com"
↓
Assign user.company = Company object
```

#### 3. **Role Assignment Logic**

The system checks in this order:

**Step 3a: Check Role Designations**
```python
# Look for email in CompanyRoleDesignation table
designation = CompanyRoleDesignation.objects.filter(
    company=company,
    email="john@acme.com",
    is_active=True
).first()

if designation exists:
    user.role = designation.role  # HR, Manager, etc.
else:
    user.role = "employee"  # Default
```

**Step 3b: If No Designation Found**
- Default role is "employee"
- HR/Manager can later update the role manually

#### 4. **Leave Balance Creation**
After role assignment, the system creates leave balances:
- Checks if company has `CompanyLeavePolicy` (custom leave days per type)
- If yes: Creates balances based on company policy
- If no: Creates balances using `LeaveType.default_allocation`

### How to Set Up HR/Manager Roles

#### Option 1: Pre-Designate Emails (Recommended)
1. HR/Manager logs in and goes to `/company/roles/`
2. Adds email addresses that should get specific roles:
   - `hr@acme.com` → Role: HR
   - `manager@acme.com` → Role: Manager
3. When these users sign up, they automatically get the designated role

#### Option 2: Manual Assignment
1. HR/Manager goes to `/company/users/`
2. Finds the user in the list
3. Changes their role using the dropdown
4. Role is updated immediately

### Example Flow

**Scenario: New HR Manager Joins**

1. **Before Signup:**
   - HR admin adds `newhr@acme.com` with role "HR" in `/company/roles/`

2. **User Signs Up:**
   - User signs up with Google using `newhr@acme.com`
   - System finds company "acme.com"
   - System finds designation for `newhr@acme.com` → Role: HR
   - User is assigned as HR immediately

3. **Result:**
   - User can access HR dashboard
   - User can manage company roles
   - User can approve/reject leave requests

### Important Notes

- **First User:** The first person to register a company becomes HR automatically
- **Domain Matching:** Users are grouped by email domain (e.g., all @acme.com users belong to Acme company)
- **Role Hierarchy:** Admin > HR > Manager > Employee
- **Permissions:** Only HR/Admin/Manager can manage roles and view company users

### Database Tables Involved

1. **Company** - Stores company information and domain
2. **CompanyRoleDesignation** - Maps email addresses to roles for a company
3. **User** - Stores user information including role and company

### Code Location

The role assignment logic is in:
- `core/signals.py` - `create_user_profile()` function (runs on user signup)
- `core/models.py` - `CompanyRoleDesignation` model
- `core/views.py` - Role management views

