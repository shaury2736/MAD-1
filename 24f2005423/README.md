# PlaceIITM – Campus Placement Portal
## IITM MAD-1 Project

A full-featured placement portal built with **Flask + SQLite + Jinja2 + Bootstrap**.

---

## 🚀 Quick Setup

```bash
# 1. Install dependencies
pip install flask werkzeug

# 2. Run the app (database auto-creates)
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

---

## 🔑 Default Admin Credentials
| Field    | Value              |
|----------|--------------------|
| Email    | admin@iitm.ac.in   |
| Password | admin123           |

---

## 👥 Roles

### Admin
- Dashboard with stats
- Approve/reject company registrations
- Approve/reject placement drives
- Blacklist/delete students & companies
- Search by name or ID
- View all applications

### Company
- Register & await admin approval
- Create/edit/delete placement drives
- View applicants per drive
- Update application status (Shortlisted / Selected / Rejected)

### Student
- Self-register & log in
- View approved drives with details
- Apply for drives (no duplicates)
- Track application status
- Edit profile & upload resume

---

## 📁 Folder Structure
```
placement_portal/
├── app.py               # Main Flask app + routes
├── database.py          # DB init & helper
├── requirements.txt
├── placement_portal.db  # Auto-created on first run
├── static/
│   └── uploads/         # Resume uploads
└── templates/
    ├── base.html
    ├── index.html
    ├── login.html
    ├── register_student.html
    ├── register_company.html
    ├── admin/
    │   ├── dashboard.html
    │   ├── companies.html
    │   ├── students.html
    │   ├── drives.html
    │   └── applications.html
    ├── company/
    │   ├── dashboard.html
    │   ├── create_drive.html
    │   ├── edit_drive.html
    │   └── applicants.html
    └── student/
        ├── dashboard.html
        └── profile.html
```

---

## 🛠 Tech Stack
| Layer     | Technology                     |
|-----------|-------------------------------|
| Backend   | Flask (Python)                |
| Database  | SQLite (auto-created)         |
| ORM       | Raw sqlite3 (no SQLAlchemy)   |
| Frontend  | Jinja2 + HTML + Bootstrap 5   |
| Auth      | Session-based (werkzeug hash) |
| Upload    | werkzeug.utils                |

---

## 🔌 API Endpoints
| Endpoint           | Auth    | Returns                     |
|--------------------|---------|------------------------------|
| GET /api/stats     | Admin   | JSON stats                  |
| GET /api/drives    | Public  | JSON approved drives         |
