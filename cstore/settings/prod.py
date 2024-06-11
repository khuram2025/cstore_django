from .base import *
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'channabdb'),
        'USER': os.getenv('DB_USER', 'channab'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'Read@123'),
        'HOST': os.getenv('DB_HOST', 'localhost'),  # Or the IP address of your PostgreSQL server
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')  
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'collected_static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'store.channab.com','*']  # Replace 'yourdomain.com' with your actual domain
