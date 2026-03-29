"""
Configuration settings for PlaceIITM Campus Placement Portal
"""

import os

# Flask Configuration
SECRET_KEY = 'iitm_placement_portal_secret_2024'
DEBUG = True

# Database Configuration
DATABASE = 'placement_portal.db'

# Upload Configuration
UPLOAD_FOLDER = 'static/uploads'
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size

# File Upload Allowed Extensions
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

# Application Settings
PREFERRED_DATE_FORMAT = '%Y-%m-%d'
SESSION_TIMEOUT = 3600  # 1 hour in seconds
