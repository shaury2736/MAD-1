"""
Utility Functions and Decorators for PlaceIITM Campus Placement Portal
"""

from functools import wraps
from flask import redirect, url_for, session, flash
from config import ALLOWED_EXTENSIONS

def login_required(f):
    """Decorator to ensure user is logged in"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """Decorator to ensure user has admin role"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def company_required(f):
    """Decorator to ensure user has company role"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'company':
            flash('Company access required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def student_required(f):
    """Decorator to ensure user has student role"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'student':
            flash('Student access required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def allowed_file(filename):
    """
    Check if uploaded file has allowed extension
    
    Args:
        filename (str): Name of the file to check
        
    Returns:
        bool: True if file extension is allowed, False otherwise
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
