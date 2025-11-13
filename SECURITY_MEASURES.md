# Security Measures in LeaveSync

## Overview
This document explains the security measures implemented to prevent abuse and unauthorized actions.

## 🔒 Security Features Implemented

### 1. **Self-Approval Prevention**
**Problem:** Users could approve their own leave requests if they became HR/Manager.

**Solution:**
- ✅ Users **cannot approve their own leave requests**
- ✅ Backend validation checks if `leave.user == request.user`
- ✅ Frontend hides approve/reject buttons for own requests
- ✅ Error message: "You cannot approve your own leave request. Please ask another HR/Manager to review it."

**Code Location:** `core/views.py` - `approve_leave()` function

---

### 2. **Self-Role-Designation Prevention**
**Problem:** Users could designate their own email as HR/Manager and then approve their own leaves.

**Solution:**
- ✅ Users **cannot designate their own email address**
- ✅ System checks: `designation_email == request.user.email`
- ✅ Error message prompts user to ask another HR/Admin

**Code Location:** `core/views.py` - `manage_company_roles()` function

---

### 3. **Email Domain Verification**
**Problem:** Users could register fake companies or designate emails from different domains.

**Solution:**
- ✅ **Company Registration:** User's email domain must match company domain
  - Example: `john@acme.com` can only register `acme.com` company
- ✅ **Role Designation:** Designated emails must match company domain
  - Example: Can only designate `@acme.com` emails for `acme.com` company
- ✅ Prevents cross-company role assignment

**Code Location:** 
- `core/views.py` - `register_company()` function
- `core/views.py` - `manage_company_roles()` function

---

### 4. **Self-Role-Change Prevention**
**Problem:** Users could change their own role to HR/Manager/Admin.

**Solution:**
- ✅ Users **cannot change their own role** to HR/Manager/Admin
- ✅ Can only change roles of other users
- ✅ Only HR/Admin can assign HR/Manager roles to others
- ✅ Error message: "You cannot change your own role to HR/Manager/Admin"

**Code Location:** `core/views.py` - `company_users()` function

---

### 5. **Company Isolation**
**Problem:** HR from one company could approve leaves from another company.

**Solution:**
- ✅ HR/Managers can only approve leaves from **their own company**
- ✅ Backend validation: `leave.user.company == request.user.company`
- ✅ Prevents cross-company approval

**Code Location:** `core/views.py` - `approve_leave()` and `reject_leave()` functions

---

### 6. **Existing User Protection**
**Problem:** Users could designate emails of existing users, causing conflicts.

**Solution:**
- ✅ Cannot designate emails of **existing users**
- ✅ System checks if user already exists before designation
- ✅ Prompts to use manual role assignment instead

**Code Location:** `core/views.py` - `manage_company_roles()` function

---

## 🛡️ Security Flow Example

### Scenario: User tries to abuse the system

1. **User signs up** with `fake@acme.com`
2. **Tries to register company** `evil.com`:
   - ❌ **BLOCKED:** Email domain (`acme.com`) doesn't match company domain (`evil.com`)
   
3. **Tries to register company** `acme.com`:
   - ✅ **ALLOWED:** Domain matches, becomes HR
   
4. **Tries to designate own email** as Manager:
   - ❌ **BLOCKED:** Cannot designate own email
   
5. **Tries to designate** `fake@evil.com`:
   - ❌ **BLOCKED:** Email domain doesn't match company domain
   
6. **Tries to designate** `colleague@acme.com`:
   - ✅ **ALLOWED:** Domain matches, not own email
   
7. **Applies for leave** and tries to approve it:
   - ❌ **BLOCKED:** Cannot approve own leave request
   - ✅ Must ask another HR/Manager to approve

---

## 🔐 Best Practices for Admins

1. **Verify Company Registration:**
   - Check that company domain matches user's email domain
   - Verify company details before marking as verified

2. **Monitor Role Assignments:**
   - Review role designations regularly
   - Ensure only legitimate emails are designated

3. **Audit Trail:**
   - All role changes are logged with `designated_by` field
   - All leave approvals are logged with `reviewed_by` field

4. **Multi-Person Approval:**
   - For sensitive operations, require multiple HR/Managers
   - Consider implementing approval workflows for high-value leaves

---

## 🚨 What's Still Vulnerable?

### Current Limitations:
1. **First Company Registrant:** First person to register a company becomes HR automatically
   - **Mitigation:** Domain verification ensures they own the email domain
   - **Recommendation:** Admin should verify companies before marking as verified

2. **No Email Verification:** System doesn't verify email ownership
   - **Mitigation:** Domain matching prevents most abuse
   - **Future Enhancement:** Add email verification step

3. **Single HR Risk:** If only one HR exists, they can't approve their own leaves
   - **Mitigation:** System prevents self-approval
   - **Recommendation:** Always have at least 2 HR/Managers per company

---

## 📝 Summary

The system now has **multiple layers of security**:
- ✅ No self-approval
- ✅ No self-role-designation  
- ✅ Domain verification
- ✅ Company isolation
- ✅ Role change restrictions

**Result:** Users cannot easily abuse the system to approve their own leaves or gain unauthorized privileges.

