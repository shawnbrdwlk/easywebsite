
import os

def get_port():
    return int(os.getenv('FLASK_PORT', 5001))

def get_debug():
    return os.getenv('FLASK_DEBUG', 'True').lower() == 'true'