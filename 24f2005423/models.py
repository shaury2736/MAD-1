"""
Database Models/Schema for PlaceIITM Campus Placement Portal
Defines the structure of all database tables
"""

# Database Schema Definitions

ADMIN_TABLE = '''
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
'''

COMPANIES_TABLE = '''
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        hr_contact TEXT,
        website TEXT,
        industry TEXT,
        description TEXT,
        approval_status TEXT DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

STUDENTS_TABLE = '''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        roll_no TEXT UNIQUE,
        branch TEXT,
        cgpa REAL DEFAULT 0.0,
        phone TEXT,
        bio TEXT,
        skills TEXT,
        resume TEXT,
        is_blacklisted INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
'''

PLACEMENT_DRIVES_TABLE = '''
    CREATE TABLE IF NOT EXISTS placement_drives (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        job_title TEXT NOT NULL,
        job_description TEXT,
        eligibility_criteria TEXT,
        application_deadline TEXT,
        package TEXT,
        location TEXT,
        status TEXT DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
    )
'''

APPLICATIONS_TABLE = '''
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        drive_id INTEGER NOT NULL,
        status TEXT DEFAULT 'applied',
        applied_date TEXT,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
        FOREIGN KEY (drive_id) REFERENCES placement_drives(id) ON DELETE CASCADE,
        UNIQUE(student_id, drive_id)
    )
'''

# List of all tables for easy initialization
ALL_TABLES = [
    ADMIN_TABLE,
    COMPANIES_TABLE,
    STUDENTS_TABLE,
    PLACEMENT_DRIVES_TABLE,
    APPLICATIONS_TABLE,
]

# Table names for reference
TABLE_NAMES = {
    'admin': 'admin',
    'companies': 'companies',
    'students': 'students',
    'placement_drives': 'placement_drives',
    'applications': 'applications',
}

# Status codes for different entities
APPROVAL_STATUSES = ['pending', 'approved', 'rejected', 'blacklisted']
APPLICATION_STATUSES = ['applied', 'shortlisted', 'selected', 'rejected']
DRIVE_STATUSES = ['pending', 'approved', 'rejected', 'closed']

# Branches for students
BRANCHES = [
    'Computer Science',
    'Data Science',
    'Electrical Engineering',
    'Mechanical Engineering',
    'Civil Engineering',
    'Electronics',
    'Management'
]

# Industries for companies
INDUSTRIES = [
    'Technology',
    'Finance & Banking',
    'Consulting',
    'E-Commerce',
    'Manufacturing',
    'Healthcare',
    'Education',
    'Government/PSU',
    'Other'
]
