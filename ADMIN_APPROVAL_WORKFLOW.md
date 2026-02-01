# 🛡️ PLATFORM ADMIN - TURF OWNER APPROVAL SCREEN
**Date:** 2026-02-01  
**Architect:** Senior UX & Backend Engineer  
**Objective:** Enable rapid, safe, and accountable approval of turf owner applications.

---

## 🏗️ ARCHITECTURE OVERVIEW

The approval workflow has been redesigned to separate **listing** from **decision making**.

### 1. The List View (`/platform-admin/pending-owners/`)
- **Role:** Triage queue.
- **Design:** Clean table showing Applicant Name, Date, and Business Name.
- **Action:** Single primary action: **"Review Application"**.
- **Change:** Removed inline "Approve" button to prevent accidental clicks without review.

### 2. The Decision Screen (`/platform-admin/review-application/<id>/`)
- **Role:** Detailed moderation interface.
- **Layout:** Split viewing pane (Left) + Sticky Action Panel (Right).
- **Key Features:**
  - **Read-Only Data:** Admin cannot accidentally edit owner details here.
  - **Google Maps Preview:** Verify location without leaving the page.
  - **Photo Gallery:** Quick quality check of uploaded venue images.
  - **Rejection Modal:** Requires a reason for rejection (compliance).

### 3. The Backend Logic (`core/views.py`)
- **Audit Logging:** Every decision (Approve/Reject) is recorded in `AdminActionLog`.
- **Transaction Safety:** `atomic()` blocks ensure user approval and turf activation happen together.
- **Data Integrity:** Rejection cascades to delete the user account (clean slate).

---

## 🎨 SCREEN LAYOUT DETAILS

### Left Panel: Application Review
| Section | Content | Purpose |
|---------|---------|---------|
| **Status Card** | Application Date, Badge | Quick context on wait time. |
| **Contact Info** | Name, Phone, Email | Verify owner identity. |
| **Turf Details** | Name, Price, Sports, City | Ensure business looks legitimate. |
| **Location** | Address, Map Link, Lat/Lng | Confirm physical existence. |
| **Photos** | Grid of uploaded images | effective quality control. |

### Right Sticky Panel: Admin Actions
| Component | Function |
|-----------|----------|
| **Checklist** | Reminder of standard verification steps (Photos, Pricing, etc). |
| **Approve Btn** | **Primary Action.** Activates User + Turf immediately. |
| **Reject Btn** | **Destructive Action.** Opens modal forcing a reason input. |
| **Stats** | Quick summary (image count, sports count) for heuristic checking. |

---

## 🔐 AUDIT & SECURITY

### `AdminActionLog` Model
We now track every "God Mode" action taken by admins.

| Field | Description |
|-------|-------------|
| `admin_user` | Who made the decision? |
| `action` | `OWNER_APPROVED` / `OWNER_REJECTED` |
| `target_user` | Who was the applicant? |
| `reason` | Why was it rejected? (or approval summary) |
| `timestamp` | When did it happen? |

**Viewable In:** `/admin/core/adminactionlog/` (Django Admin)

### Safety Measures
1. **CSRF Protection:** All actions require POST requests with tokens.
2. **Staff Only:** Protected by `@user_passes_test(lambda u: u.is_staff)`.
3. **Confirmation:** JS `confirm()` dialog on Approval.
4. **Modal:** Forced Reason input on Rejection.

---

## 🚀 HOW TO TEST

1. **Submit Application:**
   - Go to `/register-partner/` as a new user.
   - Fill form (remember: video upload removed).

2. **Access Admin:**
   - Login as Superuser.
   - Go to `/platform-admin/pending-owners/`.

3. **Review:**
   - Click "Review Application".
   - Verify layout (Left info, Right actions).

4. **Approve:**
   - Click "Approve & Activate".
   - Confirm dialog.
   - Verify User & Turf are now `is_active=True`.
   - Check `AdminActionLog` in Django Admin.

5. **Reject (Alternative):**
   - Click "Reject".
   - Type reason "Blurry photos".
   - Confirm.
   - Verify User is deleted.
   - Check `AdminActionLog` for rejection record.

---

## ✅ FINAL VERDICT

The new screen transforms a "database edit" task into a **professional moderation workflow**. It is designed for speed (<60s decision) while maintaining strict accountability and data safety.
