import os

class Config:
    """Central configuration for Bookmark Manager."""
    
    # Flask Settings
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = FLASK_ENV == 'development'
    PORT = int(os.environ.get('PORT', 5000))
    HOST = os.environ.get('HOST', '0.0.0.0')
    
    # Database Settings
    # Using relative paths. Standard execution expects CWD to be project root.
    DATABASE_NAME = os.environ.get('DATABASE_NAME', 'bookmarks.db')
    
    if FLASK_ENV == 'testing':
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    else:
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_NAME}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'connect_args': {'timeout': 30}}
    
    # API Settings
    API_BASE_URL = os.environ.get('API_BASE_URL', '') 

    # Profile Settings
    FIREFOX_PROFILE_PATH = os.environ.get('FIREFOX_PROFILE_PATH')
    CHROME_PROFILE_PATH = os.environ.get('CHROME_PROFILE_PATH')
