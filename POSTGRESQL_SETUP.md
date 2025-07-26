# PostgreSQL Database Setup Instructions

## 1. Install PostgreSQL
Download and install PostgreSQL from: https://www.postgresql.org/download/windows/

## 2. Create Database
After installation, open psql (PostgreSQL shell) and run:
```sql
CREATE DATABASE businessmanager_db;
CREATE USER businessuser WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE businessmanager_db TO businessuser;
```

## 3. Update Django Settings
The settings.py file has been updated to use PostgreSQL. Please update the password in:
BusinessManager/BusinessManager/settings.py

Change this line:
'PASSWORD': 'your_password_here',

To your actual PostgreSQL password.

## 4. Install Required Dependencies
Run in the project root directory:
```bash
pipenv install psycopg2-binary
```

## 5. Run Migrations
After database setup, run:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

## 6. Environment Variables (Recommended)
For production, consider using environment variables for database credentials:

Create a .env file:
```
DB_NAME=businessmanager_db
DB_USER=businessuser
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

And install python-decouple:
```bash
pipenv install python-decouple
```

Then update settings.py to use:
```python
from decouple import config

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}
```
